version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Paper B Doomloop specifications without state controls. Horizon 1 is the
* retained Section 4 specification; horizon 2 refreshes the historical snapshot.
* This is the only Doomloop estimation entry point used by the unified workflow.
* It is self-contained: source-only fields are merged into the empirical-theta
* panel, the debt cutoff is selected in the no-b full-control equation, and the
* readiness-change equation uses that debt cutoff without an own-cutoff search
* or a lagged-readiness state control on the right-hand side.
* The competing-criterion test replaces theta with b, mA, YA, and b*mA on one
* locked debt sample and selects the RSS-minimizing cutoff for each criterion.
* -----------------------------------------------------------------------------

args project horizon
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0805"
if "`horizon'"=="" local horizon "1"
capture confirm integer number `horizon'
if _rc | !inlist(`horizon',1,2) {
    display as error "Horizon must be 1 or 2."
    exit 198
}
local sourcefile "`project'/data0804/invest_panel_weo.csv"
local thetafile  "`project'/empirical_theta/stata_outputs/empirical_theta_panel.dta"
local workflowdir "`project'/doomloop"
if `horizon'==2 local workflowdir "`project'/doomloop_forward"
local outdir "`workflowdir'/stata_outputs"
local figuredir "`workflowdir'/figures"

capture mkdir "`workflowdir'"
capture mkdir "`outdir'"
capture mkdir "`figuredir'"
capture log close _all
log using "`outdir'/doomloop_no_state.log", text replace name(nostatelog)

display as text "DOOMLOOP NO-STATE ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "SOURCE: `sourcefile'"
display as text "THETA INPUT: `thetafile'"
display as text "OUTCOME HORIZON: ln_debt(t+`horizon'); one-year readiness change ending at t+`=`horizon'-1'"
display as text "STATE CONTROLS: b_it and lagged A omitted from regressors; debt-equation cutoff only."
display as text "COMPETING CRITERIA: theta, b, mA, YA, and b*mA on one locked debt sample."

capture confirm file "`sourcefile'"
if _rc {
    display as error "Source CSV not found."
    log close nostatelog
    exit 601
}
capture confirm file "`thetafile'"
if _rc {
    display as error "Empirical-theta panel not found. Run empirical_theta.do first."
    log close nostatelog
    exit 601
}

* Source-only interest/revenue field and source-key audit.
import delimited using "`sourcefile'", clear varnames(1) case(preserve) encoding(UTF-8)
compress
count
scalar N_source = r(N)
duplicates tag iso3 year, generate(__dup_source)
quietly count if __dup_source>0
scalar N_duplicate_source = r(N)
preserve
    keep if __dup_source>0
    keep country_name iso3 year __dup_source
    sort iso3 year
    export delimited using "`outdir'/duplicate_country_year.csv", replace
restore
if scalar(N_duplicate_source)>0 {
    display as error "Duplicate source country-year keys found."
    log close nostatelog
    exit 459
}

confirm variable interest_revenue
recast double interest_revenue
quietly summarize interest_revenue, meanonly
scalar interest_source_min = r(min)
scalar interest_source_max = r(max)
generate double __interest_source = interest_revenue
replace interest_revenue = interest_revenue/100
generate double __interest_scale_diff = abs(interest_revenue-__interest_source/100) if !missing(__interest_source)
quietly summarize __interest_scale_diff, meanonly
scalar interest_scale_maxdiff = cond(r(N)>0,r(max),0)
quietly summarize interest_revenue, meanonly
tempname p_units
postfile `p_units' str32 variable double source_min source_max ratio_min ratio_max max_abs_scaling_diff byte passed using "`outdir'/unit_scaling_checks.dta", replace
post `p_units' ("interest_revenue") (scalar(interest_source_min)) (scalar(interest_source_max)) (r(min)) (r(max)) (scalar(interest_scale_maxdiff)) (scalar(interest_scale_maxdiff)<=1e-12)
postclose `p_units'
preserve
    use "`outdir'/unit_scaling_checks.dta", clear
    format source_min source_max ratio_min ratio_max max_abs_scaling_diff %21.15g
    export delimited using "`outdir'/unit_scaling_checks.csv", replace datafmt
restore
drop __interest_source __interest_scale_diff __dup_source
keep iso3 year interest_revenue
tempfile source_extra
save `source_extra', replace

* Empirical theta, exact panel timing, and construction audit.
use "`thetafile'", clear
compress
isid iso3 year
merge 1:1 iso3 year using `source_extra', assert(match) nogen
isid iso3 year

foreach v in ln_debt b_it_theta mA_hat ln_debt_mA_hat YA_hat theta_hat_A readiness100 vulnerability100 growth ln_constantgdp inflation_cpi reserves tt country_id {
    capture confirm variable `v'
    if _rc {
        display as error "Required variable missing from the merged theta panel: `v'"
        log close nostatelog
        exit 111
    }
}
generate double theta_recomputed_ln_debt = ln_debt_mA_hat+YA_hat if !missing(ln_debt_mA_hat,YA_hat)
generate double theta_reconstruction_diff = abs(theta_hat_A-theta_recomputed_ln_debt) if !missing(theta_hat_A,theta_recomputed_ln_debt)
generate double b_it_mapping_diff = abs(b_it_theta-ln_debt) if !missing(b_it_theta,ln_debt)
quietly summarize theta_reconstruction_diff, meanonly
scalar max_theta_reconstruction_diff_ns = cond(r(N)>0,r(max),.)
quietly summarize b_it_mapping_diff, meanonly
scalar max_b_it_mapping_diff_ns = cond(r(N)>0,r(max),.)
quietly count if b_it_theta!=ln_debt
scalar bad_b_it_mapping_rows_ns = r(N)
if scalar(max_theta_reconstruction_diff_ns)>1e-10 | scalar(max_b_it_mapping_diff_ns)>1e-10 | scalar(bad_b_it_mapping_rows_ns)>0 {
    display as error "Theta is not ln_debt*mA_hat + YA_hat, or b_it is not ln_debt."
    log close nostatelog
    exit 459
}
label variable theta_recomputed_ln_debt "ln_debt*mA_hat + YA_hat recomputed in doomloop"
label variable theta_reconstruction_diff "Absolute theta reconstruction difference"
label variable b_it_mapping_diff "Absolute difference between b_it alias and ln_debt"

xtset country_id year
if `horizon'==1 generate double b_outcome = F.ln_debt-ln_debt if !missing(F.ln_debt,ln_debt)
if `horizon'==2 generate double b_outcome = F2.ln_debt-ln_debt if !missing(F2.ln_debt,ln_debt)
generate int b_outcome_year = year+`horizon' if !missing(b_outcome)
generate double readiness_lag = L.readiness100
if `horizon'==1 generate double A_outcome = readiness100-readiness_lag if !missing(readiness100,readiness_lag)
if `horizon'==2 generate double A_outcome = F.readiness100-readiness100 if !missing(F.readiness100,readiness100)
generate int A_outcome_year = year+`horizon'-1 if !missing(A_outcome)
label variable b_outcome "Change in log government debt from t to t+h"
label variable readiness_lag "Readiness A at t-1 from exact panel lag"
label variable A_outcome "One-year change in readiness ending at t+h-1"

local xcontrol vulnerability100
local always_controls growth ln_constantgdp
local macro_debt inflation_cpi
local macro_ready inflation_cpi
local external reserves tt
local controls_debt `macro_debt' `external'
local controls_ready `macro_ready' `external'
local full_controls_debt `xcontrol' `always_controls' `controls_debt'
local full_controls_ready `xcontrol' `always_controls' `controls_ready'

* The debt sample contains every competing criterion so RSS values are comparable.
local debt_required b_outcome readiness100 theta_hat_A ln_debt mA_hat YA_hat ln_debt_mA_hat `full_controls_debt'
local ready_required A_outcome interest_revenue theta_hat_A `full_controls_ready'
egen int debt_ns_missing_count = rowmiss(`debt_required')
egen int ready_ns_missing_count = rowmiss(`ready_required')
generate byte sample_debt_ns = debt_ns_missing_count==0
generate byte sample_ready_ns = ready_ns_missing_count==0
label variable sample_debt_ns "Locked debt sample for all five cutoff criteria"
label variable sample_ready_ns "Locked readiness-change sample without lagged-A state control"

quietly count if sample_debt_ns
scalar N_debt_ns = r(N)
quietly count if sample_ready_ns
scalar N_ready_ns = r(N)
if scalar(N_debt_ns)==0 | scalar(N_ready_ns)==0 {
    display as error "A locked Doomloop sample is empty."
    log close nostatelog
    exit 2000
}
egen byte tag_country_debt_ns = tag(country_id) if sample_debt_ns
egen byte tag_year_debt_ns = tag(year) if sample_debt_ns
egen byte tag_country_ready_ns = tag(country_id) if sample_ready_ns
egen byte tag_year_ready_ns = tag(year) if sample_ready_ns
quietly count if tag_country_debt_ns==1
scalar G_debt_ns = r(N)
quietly count if tag_year_debt_ns==1
scalar T_debt_ns = r(N)
quietly summarize year if sample_debt_ns, meanonly
scalar year_min_debt_ns = r(min)
scalar year_max_debt_ns = r(max)
quietly count if tag_country_ready_ns==1
scalar G_ready_ns = r(N)
quietly count if tag_year_ready_ns==1
scalar T_ready_ns = r(N)
quietly summarize year if sample_ready_ns, meanonly
scalar year_min_ready_ns = r(min)
scalar year_max_ready_ns = r(max)

* Descriptive statistics and data-quality diagnostics on locked samples.
tempname p_desc
postfile `p_desc' str12 equation str32 variable double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/nostate_descriptive_stats.dta", replace
foreach eq in debt ready {
    local flag sample_`eq'_ns
    if "`eq'"=="debt" local vars b_outcome theta_hat_A ln_debt mA_hat YA_hat ln_debt_mA_hat readiness100 `full_controls_debt'
    if "`eq'"=="ready" local vars A_outcome theta_hat_A interest_revenue `full_controls_ready'
    foreach v of local vars {
        quietly summarize `v' if `flag', detail
        post `p_desc' ("`eq'") ("`v'") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    }
}
postclose `p_desc'
preserve
    use "`outdir'/nostate_descriptive_stats.dta", clear
    export delimited using "`outdir'/nostate_descriptive_stats.csv", replace
restore

tempname p_var
postfile `p_var' str12 equation str32 variable double sd_overall sd_between sd_within ratio_within_overall str24 fe_identification using "`outdir'/nostate_variation.dta", replace
foreach eq in debt ready {
    local flag sample_`eq'_ns
    if "`eq'"=="debt" local vars b_outcome theta_hat_A ln_debt mA_hat YA_hat ln_debt_mA_hat readiness100 `full_controls_debt'
    if "`eq'"=="ready" local vars A_outcome theta_hat_A interest_revenue `full_controls_ready'
    foreach v of local vars {
        quietly xtsum `v' if `flag'
        local sdo = r(sd)
        local sdb = r(sd_b)
        local sdw = r(sd_w)
        local ratio = cond(`sdo'>0,`sdw'/`sdo',.)
        local ident "adequate"
        if missing(`sdw') | `sdw'<=1e-10*max(1,`sdo') local ident "not_identified_by_FE"
        else if `ratio'<.01 local ident "low_within_variation"
        post `p_var' ("`eq'") ("`v'") (`sdo') (`sdb') (`sdw') (`ratio') ("`ident'")
    }
}
postclose `p_var'
preserve
    use "`outdir'/nostate_variation.dta", clear
    export delimited using "`outdir'/nostate_variation.csv", replace
restore

tempname p_miss
postfile `p_miss' str12 equation str32 variable double missing_total missing_rate exclusive_loss using "`outdir'/nostate_missing_loss.dta", replace
foreach eq in debt ready {
    if "`eq'"=="debt" local vars `debt_required'
    if "`eq'"=="ready" local vars `ready_required'
    foreach v of local vars {
        local others : list vars - v
        quietly count if missing(`v')
        local mt = r(N)
        capture drop __other_missing
        egen int __other_missing = rowmiss(`others')
        quietly count if missing(`v') & __other_missing==0
        local ex = r(N)
        post `p_miss' ("`eq'") ("`v'") (`mt') (100*`mt'/scalar(N_source)) (`ex')
    }
}
capture drop __other_missing
postclose `p_miss'
preserve
    use "`outdir'/nostate_missing_loss.dta", clear
    export delimited using "`outdir'/nostate_missing_loss.csv", replace
restore

* Formula-check postfile remains open during criterion estimation so the exact
* regressors used in every search can be compared with their defining formula.
tempname p_formula
postfile `p_formula' str64 check double max_abs_difference tolerance byte passed using "`outdir'/nostate_formula_checks.dta", replace
post `p_formula' ("theta uses ln_debt*mA_hat + YA_hat") (scalar(max_theta_reconstruction_diff_ns)) (1e-10) (scalar(max_theta_reconstruction_diff_ns)<=1e-10)
post `p_formula' ("b_it maps exactly to ln_debt") (scalar(max_b_it_mapping_diff_ns)) (1e-10) (scalar(max_b_it_mapping_diff_ns)<=1e-10 & scalar(bad_b_it_mapping_rows_ns)==0)
generate double __A_outcome_formula = .
if `horizon'==1 replace __A_outcome_formula = readiness100-readiness_lag if !missing(A_outcome)
if `horizon'==2 replace __A_outcome_formula = F.readiness100-readiness100 if !missing(A_outcome)
generate double __A_outcome_diff = abs(A_outcome-__A_outcome_formula) if !missing(A_outcome)
quietly summarize __A_outcome_diff, meanonly
post `p_formula' ("readiness outcome is exact one-year change") (r(max)) (1e-12) (r(max)<=1e-12)
drop __A_outcome_formula __A_outcome_diff

* -----------------------------------------------------------------------------
* Criterion Decomposition / Competing Criterion Test.
* -----------------------------------------------------------------------------
tempname p_profile p_compare
postfile `p_profile' str12 criterion str32 variable double cutoff rss N N_low N_high using "`outdir'/criterion_rss_profiles.dta", replace
postfile `p_compare' str12 criterion str32 variable double cutoff beta_L p_L beta_H p_H str24 theoretical_signs double rss r2_within N N_low N_high candidate_count trim_low trim_high using "`outdir'/criterion_comparison.dta", replace

local criterion_keys theta debt ma ya bma
foreach key of local criterion_keys {
    if "`key'"=="theta" {
        local qvar theta_hat_A
        local qlabel "theta"
    }
    if "`key'"=="debt" {
        local qvar ln_debt
        local qlabel "b"
    }
    if "`key'"=="ma" {
        local qvar mA_hat
        local qlabel "mA"
    }
    if "`key'"=="ya" {
        local qvar YA_hat
        local qlabel "YA"
    }
    if "`key'"=="bma" {
        local qvar ln_debt_mA_hat
        local qlabel "b*mA"
    }

    quietly summarize `qvar' if sample_debt_ns, detail
    scalar q_min_`key' = r(min)
    scalar q_p1_`key' = r(p1)
    scalar q_p10_`key' = r(p10)
    scalar q_p25_`key' = r(p25)
    scalar q_p50_`key' = r(p50)
    scalar q_mean_`key' = r(mean)
    scalar q_p75_`key' = r(p75)
    scalar q_p90_`key' = r(p90)
    scalar q_p99_`key' = r(p99)
    scalar q_max_`key' = r(max)
    format `qvar' %21.15g
    quietly levelsof `qvar' if sample_debt_ns & `qvar'>=scalar(q_p10_`key') & `qvar'<=scalar(q_p90_`key'), local(candidates) clean

    scalar rss_min_`key' = .
    scalar cutoff_`key' = .
    scalar candidate_count_`key' = 0
    scalar low_n_`key' = .
    scalar high_n_`key' = .
    generate double __hL = .
    generate double __hH = .
    generate double __xL = .
    generate double __xH = .
    local minside = max(50,ceil(.10*scalar(N_debt_ns)))

    foreach c of local candidates {
        quietly count if sample_debt_ns & `qvar'<=`c'
        local nlow = r(N)
        quietly count if sample_debt_ns & `qvar'>`c'
        local nhigh = r(N)
        if `nlow'>=`minside' & `nhigh'>=`minside' {
            quietly replace __hL = max(`c'-`qvar',0) if sample_debt_ns
            quietly replace __hH = max(`qvar'-`c',0) if sample_debt_ns
            quietly replace __xL = readiness100*__hL if sample_debt_ns
            quietly replace __xH = readiness100*__hH if sample_debt_ns
            quietly areg b_outcome __xL __xH `full_controls_debt' i.year if sample_debt_ns, absorb(country_id)
            local this_rss = e(rss)
            post `p_profile' ("`qlabel'") ("`qvar'") (`c') (`this_rss') (e(N)) (`nlow') (`nhigh')
            scalar candidate_count_`key' = scalar(candidate_count_`key')+1
            if missing(scalar(rss_min_`key')) | `this_rss'<scalar(rss_min_`key') {
                scalar rss_min_`key' = `this_rss'
                scalar cutoff_`key' = `c'
                scalar low_n_`key' = `nlow'
                scalar high_n_`key' = `nhigh'
            }
        }
    }
    if missing(scalar(cutoff_`key')) {
        display as error "No admissible cutoff for criterion `qlabel'."
        postclose `p_profile'
        postclose `p_compare'
        postclose `p_formula'
        log close nostatelog
        exit 498
    }

    quietly replace __hL = max(scalar(cutoff_`key')-`qvar',0) if sample_debt_ns
    quietly replace __hH = max(`qvar'-scalar(cutoff_`key'),0) if sample_debt_ns
    quietly replace __xL = readiness100*__hL if sample_debt_ns
    quietly replace __xH = readiness100*__hH if sample_debt_ns
    generate double __formula = readiness100*max(scalar(cutoff_`key')-`qvar',0) if sample_debt_ns
    generate double __diff = abs(__xL-__formula) if sample_debt_ns
    quietly summarize __diff, meanonly
    scalar formula_low_`key' = cond(r(N)>0,r(max),.)
    drop __formula __diff
    generate double __formula = readiness100*max(`qvar'-scalar(cutoff_`key'),0) if sample_debt_ns
    generate double __diff = abs(__xH-__formula) if sample_debt_ns
    quietly summarize __diff, meanonly
    scalar formula_high_`key' = cond(r(N)>0,r(max),.)
    drop __formula __diff

    quietly xtreg b_outcome __xL __xH `full_controls_debt' i.year if sample_debt_ns, fe
    local r2w = e(r2_w)
    quietly areg b_outcome __xL __xH `full_controls_debt' i.year if sample_debt_ns, absorb(country_id) vce(robust)
    local betaL = _b[__xL]
    local betaH = _b[__xH]
    local pL = 2*ttail(e(df_r),abs(_b[__xL]/_se[__xL]))
    local pH = 2*ttail(e(df_r),abs(_b[__xH]/_se[__xH]))
    local finalrss = e(rss)
    local signL = cond(`betaL'>0,"+",cond(`betaL'<0,"-","0"))
    local signH = cond(`betaH'>0,"+",cond(`betaH'<0,"-","0"))
    local theory "No (`signL',`signH')"
    if (`betaL'>0 & `betaH'<0) local theory "Match (+,-)"
    else if (`betaL'>0 | `betaH'<0) local theory "Partial (`signL',`signH')"
    post `p_compare' ("`qlabel'") ("`qvar'") (scalar(cutoff_`key')) (`betaL') (`pL') (`betaH') (`pH') ("`theory'") (`finalrss') (`r2w') (e(N)) (scalar(low_n_`key')) (scalar(high_n_`key')) (scalar(candidate_count_`key')) (scalar(q_p10_`key')) (scalar(q_p90_`key'))

    post `p_formula' ("criterion `qlabel' low hinge") (scalar(formula_low_`key')) (1e-10) (scalar(formula_low_`key')<=1e-10)
    post `p_formula' ("criterion `qlabel' high hinge") (scalar(formula_high_`key')) (1e-10) (scalar(formula_high_`key')<=1e-10)
    drop __hL __hH __xL __xH
}
postclose `p_profile'
postclose `p_compare'
foreach f in criterion_rss_profiles criterion_comparison {
    preserve
        use "`outdir'/`f'.dta", clear
        sort criterion cutoff
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

scalar rss_min_cutoff_debt_ns = scalar(cutoff_theta)
scalar rss_min_debt_ns = scalar(rss_min_theta)
scalar cutoff_candidates_debt_ns = scalar(candidate_count_theta)
scalar cutoff_low_n_debt_ns = scalar(low_n_theta)
scalar cutoff_high_n_debt_ns = scalar(high_n_theta)

* A single cutoff file: readiness inherits the debt/theta cutoff and is not a
* searched equation.
tempname p_cutoff
postfile `p_cutoff' str12 equation str16 cutoff_source double rss_min_cutoff rss candidate_count trim_low trim_high low_n high_n criterion_min criterion_max using "`outdir'/nostate_cutoffs.dta", replace
post `p_cutoff' ("debt") ("debt_full") (scalar(rss_min_cutoff_debt_ns)) (scalar(rss_min_debt_ns)) (scalar(cutoff_candidates_debt_ns)) (scalar(q_p10_theta)) (scalar(q_p90_theta)) (scalar(cutoff_low_n_debt_ns)) (scalar(cutoff_high_n_debt_ns)) (scalar(q_min_theta)) (scalar(q_max_theta))
postclose `p_cutoff'
preserve
    use "`outdir'/nostate_cutoffs.dta", clear
    export delimited using "`outdir'/nostate_cutoffs.csv", replace
restore

* Main debt and readiness hinges, both at the debt/theta cutoff.
generate double debt_hinge_low_ns = max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_debt_ns
generate double debt_hinge_high_ns = max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_debt_ns
generate double debt_kink_low = readiness100*debt_hinge_low_ns if sample_debt_ns
generate double debt_kink_high = readiness100*debt_hinge_high_ns if sample_debt_ns
generate double ready_debt_hinge_low_ns = max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_ready_ns
generate double ready_debt_hinge_high_ns = max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_ready_ns
generate double ready_debt_kink_low = interest_revenue*ready_debt_hinge_low_ns if sample_ready_ns
generate double ready_debt_kink_high = interest_revenue*ready_debt_hinge_high_ns if sample_ready_ns
quietly areg A_outcome ready_debt_kink_low ready_debt_kink_high `full_controls_ready' i.year if sample_ready_ns, absorb(country_id)
scalar rss_ready_at_debt_cutoff_ns = e(rss)

* Main-equation regression descriptives.
tempname p_regdesc
postfile `p_regdesc' str24 specification str12 equation str32 variable str24 role double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/nostate_regression_descriptive_stats.dta", replace
foreach eq in debt ready_debt {
    if "`eq'"=="debt" {
        local flag sample_debt_ns
        local spec "debt_no_b"
        local depvar b_outcome
        local regressors debt_kink_low debt_kink_high `full_controls_debt'
        local inputs readiness100 theta_hat_A ln_debt mA_hat YA_hat ln_debt_mA_hat
    }
    if "`eq'"=="ready_debt" {
        local flag sample_ready_ns
        local spec "ready_no_lag_debt_cutoff"
        local depvar A_outcome
        local regressors ready_debt_kink_low ready_debt_kink_high `full_controls_ready'
        local inputs interest_revenue theta_hat_A
    }
    quietly summarize `depvar' if `flag', detail
    post `p_regdesc' ("`spec'") ("`eq'") ("`depvar'") ("dependent_variable") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    foreach v of local regressors {
        quietly summarize `v' if `flag', detail
        post `p_regdesc' ("`spec'") ("`eq'") ("`v'") ("regressor") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    }
    foreach v of local inputs {
        quietly summarize `v' if `flag', detail
        post `p_regdesc' ("`spec'") ("`eq'") ("`v'") ("construction_input") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    }
}
postclose `p_regdesc'
preserve
    use "`outdir'/nostate_regression_descriptive_stats.dta", clear
    export delimited using "`outdir'/nostate_regression_descriptive_stats.csv", replace
restore

* Three nested columns for each unique main equation.
tempname p_stats p_coef p_equation
postfile `p_stats' str24 model str12 equation double cutoff N countries years first_year last_year r2_within r2_overall rss df_r byte macro_controls external_controls using "`outdir'/nostate_model_stats.dta", replace
postfile `p_coef' str24 model str12 equation str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/nostate_model_coefficients.dta", replace
postfile `p_equation' str24 model str244 equation_text using "`outdir'/nostate_equations.dta", replace

local dm1 "DN1_core"
local dr1 "debt_kink_low debt_kink_high `xcontrol' `always_controls'"
local dq1 "Delta b(t+`horizon'); theta kink; b_it omitted; country and year FE"
local dmc1 0
local dec1 0
local dm2 "DN2_macro"
local dr2 "debt_kink_low debt_kink_high `xcontrol' `always_controls' `macro_debt'"
local dq2 "DN1 plus inflation; growth and ln_constantgdp retained"
local dmc2 1
local dec2 0
local dm3 "DN3_full"
local dr3 "debt_kink_low debt_kink_high `full_controls_debt'"
local dq3 "DN2 plus reserves and terms of trade; b_it omitted"
local dmc3 1
local dec3 1
forvalues z=1/3 {
    local mid "`dm`z''"
    local rhs "`dr`z''"
    quietly xtreg b_outcome `rhs' i.year if sample_debt_ns, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg b_outcome `rhs' i.year if sample_debt_ns, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("debt") (scalar(rss_min_cutoff_debt_ns)) (e(N)) (scalar(G_debt_ns)) (scalar(T_debt_ns)) (scalar(year_min_debt_ns)) (scalar(year_max_debt_ns)) (`r2w') (`r2o') (e(rss)) (e(df_r)) (`dmc`z'') (`dec`z'')
    post `p_equation' ("`mid'") ("`dq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc post `p_coef' ("`mid'") ("debt") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            post `p_coef' ("`mid'") ("debt") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}

local rm1 "RDN1_core"
local rr1 "ready_debt_kink_low ready_debt_kink_high `xcontrol' `always_controls'"
local rq1 "Delta A(t+`=`horizon'-1') over one year; no lagged-A state control; debt cutoff"
local rmc1 0
local rec1 0
local rm2 "RDN2_macro"
local rr2 "ready_debt_kink_low ready_debt_kink_high `xcontrol' `always_controls' `macro_ready'"
local rq2 "RDN1 plus inflation; growth and ln_constantgdp retained"
local rmc2 1
local rec2 0
local rm3 "RDN3_full"
local rr3 "ready_debt_kink_low ready_debt_kink_high `full_controls_ready'"
local rq3 "RDN2 plus reserves and terms of trade; debt cutoff only"
local rmc3 1
local rec3 1
forvalues z=1/3 {
    local mid "`rm`z''"
    local rhs "`rr`z''"
    quietly xtreg A_outcome `rhs' i.year if sample_ready_ns, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg A_outcome `rhs' i.year if sample_ready_ns, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("ready_debt") (scalar(rss_min_cutoff_debt_ns)) (e(N)) (scalar(G_ready_ns)) (scalar(T_ready_ns)) (scalar(year_min_ready_ns)) (scalar(year_max_ready_ns)) (`r2w') (`r2o') (e(rss)) (e(df_r)) (`rmc`z'') (`rec`z'')
    post `p_equation' ("`mid'") ("`rq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc post `p_coef' ("`mid'") ("ready_debt") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            post `p_coef' ("`mid'") ("ready_debt") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}
postclose `p_stats'
postclose `p_coef'
postclose `p_equation'
foreach f in model_stats model_coefficients equations {
    preserve
        use "`outdir'/nostate_`f'.dta", clear
        export delimited using "`outdir'/nostate_`f'.csv", replace
    restore
}

* Wald tests and preferred full-control coefficients.
tempname p_wald p_key
postfile `p_wald' str24 model str80 hypothesis double F df_num df_den p using "`outdir'/nostate_wald_tests.dta", replace
postfile `p_key' str12 equation double cutoff coefficient_low p_low coefficient_high p_high product_ab byte opposite_sign using "`outdir'/nostate_key_results.dta", replace
estimates restore DN3_full
quietly test debt_kink_low debt_kink_high
post `p_wald' ("DN3_full") ("low- and high-branch coefficients jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro_debt'
post `p_wald' ("DN3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("DN3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls_debt'
post `p_wald' ("DN3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar debt_beta_L_ns = _b[debt_kink_low]
scalar debt_beta_H_ns = _b[debt_kink_high]
scalar debt_se_L_ns = _se[debt_kink_low]
scalar debt_se_H_ns = _se[debt_kink_high]
scalar debt_p_L_ns = 2*ttail(e(df_r),abs(_b[debt_kink_low]/_se[debt_kink_low]))
scalar debt_p_H_ns = 2*ttail(e(df_r),abs(_b[debt_kink_high]/_se[debt_kink_high]))
scalar debt_df_ns = e(df_r)
post `p_key' ("debt") (scalar(rss_min_cutoff_debt_ns)) (scalar(debt_beta_L_ns)) (scalar(debt_p_L_ns)) (scalar(debt_beta_H_ns)) (scalar(debt_p_H_ns)) (scalar(debt_beta_L_ns)*scalar(debt_beta_H_ns)) (scalar(debt_beta_L_ns)*scalar(debt_beta_H_ns)<0)

estimates restore RDN3_full
quietly test ready_debt_kink_low ready_debt_kink_high
post `p_wald' ("RDN3_full") ("branches jointly zero; debt-equation cutoff") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro_ready'
post `p_wald' ("RDN3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("RDN3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls_ready'
post `p_wald' ("RDN3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar ready_debt_delta_L_ns = _b[ready_debt_kink_low]
scalar ready_debt_delta_H_ns = _b[ready_debt_kink_high]
scalar ready_debt_se_L_ns = _se[ready_debt_kink_low]
scalar ready_debt_se_H_ns = _se[ready_debt_kink_high]
scalar ready_debt_p_L_ns = 2*ttail(e(df_r),abs(_b[ready_debt_kink_low]/_se[ready_debt_kink_low]))
scalar ready_debt_p_H_ns = 2*ttail(e(df_r),abs(_b[ready_debt_kink_high]/_se[ready_debt_kink_high]))
scalar ready_debt_df_ns = e(df_r)
post `p_key' ("ready_debt") (scalar(rss_min_cutoff_debt_ns)) (scalar(ready_debt_delta_L_ns)) (scalar(ready_debt_p_L_ns)) (scalar(ready_debt_delta_H_ns)) (scalar(ready_debt_p_H_ns)) (scalar(ready_debt_delta_L_ns)*scalar(ready_debt_delta_H_ns)) (scalar(ready_debt_delta_L_ns)*scalar(ready_debt_delta_H_ns)<0)
postclose `p_wald'
postclose `p_key'
foreach f in wald_tests key_results {
    preserve
        use "`outdir'/nostate_`f'.dta", clear
        export delimited using "`outdir'/nostate_`f'.csv", replace
    restore
}

* Theta support for marginal effects and figures.
quietly summarize theta_hat_A if sample_debt_ns, detail
scalar theta_debt_ns_p1 = r(p1)
scalar theta_debt_ns_p10 = r(p10)
scalar theta_debt_ns_p25 = r(p25)
scalar theta_debt_ns_p50 = r(p50)
scalar theta_debt_ns_mean = r(mean)
scalar theta_debt_ns_p75 = r(p75)
scalar theta_debt_ns_p90 = r(p90)
scalar theta_debt_ns_p99 = r(p99)
quietly summarize theta_hat_A if sample_ready_ns, detail
scalar theta_ready_ns_p1 = r(p1)
scalar theta_ready_ns_p10 = r(p10)
scalar theta_ready_ns_p25 = r(p25)
scalar theta_ready_ns_p50 = r(p50)
scalar theta_ready_ns_mean = r(mean)
scalar theta_ready_ns_p75 = r(p75)
scalar theta_ready_ns_p90 = r(p90)
scalar theta_ready_ns_p99 = r(p99)

tempname p_me
postfile `p_me' str12 equation str16 estimand str12 point double theta cutoff marginal_effect se t p ci_low ci_high using "`outdir'/nostate_marginal_effects.dta", replace
estimates restore DN3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_debt_ns_p10)
    if "`point'"=="P25" local th = scalar(theta_debt_ns_p25)
    if "`point'"=="P50" local th = scalar(theta_debt_ns_p50)
    if "`point'"=="Mean" local th = scalar(theta_debt_ns_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_debt_ns)
    if "`point'"=="P75" local th = scalar(theta_debt_ns_p75)
    if "`point'"=="P90" local th = scalar(theta_debt_ns_p90)
    if abs(`th'-scalar(rss_min_cutoff_debt_ns))<1e-12 post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (0) (0) (.) (.) (0) (0)
    else if `th'<scalar(rss_min_cutoff_debt_ns) {
        local weight = scalar(rss_min_cutoff_debt_ns)-`th'
        quietly lincom `weight'*debt_kink_low
        post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_debt_ns)
        quietly lincom `weight'*debt_kink_high
        post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}
estimates restore RDN3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_ready_ns_p10)
    if "`point'"=="P25" local th = scalar(theta_ready_ns_p25)
    if "`point'"=="P50" local th = scalar(theta_ready_ns_p50)
    if "`point'"=="Mean" local th = scalar(theta_ready_ns_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_debt_ns)
    if "`point'"=="P75" local th = scalar(theta_ready_ns_p75)
    if "`point'"=="P90" local th = scalar(theta_ready_ns_p90)
    if abs(`th'-scalar(rss_min_cutoff_debt_ns))<1e-12 post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (0) (0) (.) (.) (0) (0)
    else if `th'<scalar(rss_min_cutoff_debt_ns) {
        local weight = scalar(rss_min_cutoff_debt_ns)-`th'
        quietly lincom `weight'*ready_debt_kink_low
        post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_debt_ns)
        quietly lincom `weight'*ready_debt_kink_high
        post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}
postclose `p_me'
preserve
    use "`outdir'/nostate_marginal_effects.dta", clear
    export delimited using "`outdir'/nostate_marginal_effects.csv", replace
restore

* Main marginal-effect figures only: debt and readiness change at debt cutoff.
preserve
    clear
    set obs 202
    generate double theta = scalar(theta_debt_ns_p1)+(_n-1)*(scalar(theta_debt_ns_p99)-scalar(theta_debt_ns_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_debt_ns) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_debt_ns)
    generate double marginal_effect = cond(theta<cutoff,scalar(debt_beta_L_ns)*(cutoff-theta),scalar(debt_beta_H_ns)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(debt_se_L_ns),abs(theta-cutoff)*scalar(debt_se_H_ns))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(debt_df_ns),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/nostate_marginal_curve_debt.dta", replace
    export delimited using "`outdir'/nostate_marginal_curve_debt.csv", replace
    twoway (rarea ci_low ci_high theta, color("214 229 242")) (line marginal_effect theta, lcolor("31 119 180") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_debt_ns)', lcolor(gs6) lpattern(dash) lwidth(medthin)) yline(0, lcolor(gs8) lwidth(thin)) ///
        title("Debt/GDP change at t+`horizon': no b_it state", color(black) size(medsmall)) subtitle("Full controls; pointwise 95% CI; P1-P99 theta support", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ytitle("Marginal effect on change in debt/GDP", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) graphregion(color(white)) plotregion(color(white)) ///
        note("Dashed line: RSS-minimizing cutoff in the full debt equation.", size(vsmall) color(gs5)) name(g_debt_ns, replace)
    graph export "`figuredir'/debt_marginal_effect_no_b.png", replace width(2400)
    graph export "`figuredir'/debt_marginal_effect_no_b.pdf", replace
restore

preserve
    clear
    set obs 202
    generate double theta = scalar(theta_ready_ns_p1)+(_n-1)*(scalar(theta_ready_ns_p99)-scalar(theta_ready_ns_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_debt_ns) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_debt_ns)
    generate double marginal_effect = cond(theta<cutoff,scalar(ready_debt_delta_L_ns)*(cutoff-theta),scalar(ready_debt_delta_H_ns)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(ready_debt_se_L_ns),abs(theta-cutoff)*scalar(ready_debt_se_H_ns))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(ready_debt_df_ns),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/nostate_marginal_curve_ready_debt_cutoff.dta", replace
    export delimited using "`outdir'/nostate_marginal_curve_ready_debt_cutoff.csv", replace
    twoway (rarea ci_low ci_high theta, color("226 239 218")) (line marginal_effect theta, lcolor("44 127 55") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_debt_ns)', lcolor(gs6) lpattern(dash) lwidth(medthin)) yline(0, lcolor(gs8) lwidth(thin)) ///
        title("Readiness change A(t)-A(t-1)", color(black) size(medsmall)) subtitle("Cutoff inherited from full debt equation; pointwise 95% CI", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ytitle("Marginal effect on readiness change", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) graphregion(color(white)) plotregion(color(white)) ///
        note("Dashed line: debt-equation cutoff; no lagged-A state regressor.", size(vsmall) color(gs5)) name(g_ready_debt_ns, replace)
    graph export "`figuredir'/readiness_marginal_effect_debt_cutoff_no_lag.png", replace width(2400)
    graph export "`figuredir'/readiness_marginal_effect_debt_cutoff_no_lag.pdf", replace
restore

graph combine g_debt_ns g_ready_debt_ns, cols(1) xcommon graphregion(color(white)) imargin(tiny) name(g_nostate, replace)
graph export "`figuredir'/kink_marginal_effects_no_state.png", replace width(2400)
graph export "`figuredir'/kink_marginal_effects_no_state.pdf", replace

* Estimator validation: all five criterion branch coefficients plus readiness.
tempname p_validate
postfile `p_validate' str12 specification str12 equation str16 variable double areg_b lsdv_b abs_b_diff areg_se lsdv_se abs_se_diff using "`outdir'/nostate_estimator_validation.dta", replace
foreach key of local criterion_keys {
    if "`key'"=="theta" {
        local qvar theta_hat_A
        local qlabel "theta"
    }
    if "`key'"=="debt" {
        local qvar ln_debt
        local qlabel "b"
    }
    if "`key'"=="ma" {
        local qvar mA_hat
        local qlabel "mA"
    }
    if "`key'"=="ya" {
        local qvar YA_hat
        local qlabel "YA"
    }
    if "`key'"=="bma" {
        local qvar ln_debt_mA_hat
        local qlabel "b*mA"
    }
    generate double __vL = readiness100*max(scalar(cutoff_`key')-`qvar',0) if sample_debt_ns
    generate double __vH = readiness100*max(`qvar'-scalar(cutoff_`key'),0) if sample_debt_ns
    quietly areg b_outcome __vL __vH `full_controls_debt' i.year if sample_debt_ns, absorb(country_id) vce(robust)
    scalar ar_b_L = _b[__vL]
    scalar ar_b_H = _b[__vH]
    scalar ar_s_L = _se[__vL]
    scalar ar_s_H = _se[__vH]
    quietly regress b_outcome __vL __vH `full_controls_debt' i.country_id i.year if sample_debt_ns, vce(robust)
    post `p_validate' ("`qlabel'") ("criterion") ("beta_L") (scalar(ar_b_L)) (_b[__vL]) (abs(scalar(ar_b_L)-_b[__vL])) (scalar(ar_s_L)) (_se[__vL]) (abs(scalar(ar_s_L)-_se[__vL]))
    post `p_validate' ("`qlabel'") ("criterion") ("beta_H") (scalar(ar_b_H)) (_b[__vH]) (abs(scalar(ar_b_H)-_b[__vH])) (scalar(ar_s_H)) (_se[__vH]) (abs(scalar(ar_s_H)-_se[__vH]))
    drop __vL __vH
}
quietly areg A_outcome ready_debt_kink_low ready_debt_kink_high `full_controls_ready' i.year if sample_ready_ns, absorb(country_id) vce(robust)
scalar ar_b_L = _b[ready_debt_kink_low]
scalar ar_b_H = _b[ready_debt_kink_high]
scalar ar_s_L = _se[ready_debt_kink_low]
scalar ar_s_H = _se[ready_debt_kink_high]
quietly regress A_outcome ready_debt_kink_low ready_debt_kink_high `full_controls_ready' i.country_id i.year if sample_ready_ns, vce(robust)
post `p_validate' ("readiness") ("ready_debt") ("delta_L") (scalar(ar_b_L)) (_b[ready_debt_kink_low]) (abs(scalar(ar_b_L)-_b[ready_debt_kink_low])) (scalar(ar_s_L)) (_se[ready_debt_kink_low]) (abs(scalar(ar_s_L)-_se[ready_debt_kink_low]))
post `p_validate' ("readiness") ("ready_debt") ("delta_H") (scalar(ar_b_H)) (_b[ready_debt_kink_high]) (abs(scalar(ar_b_H)-_b[ready_debt_kink_high])) (scalar(ar_s_H)) (_se[ready_debt_kink_high]) (abs(scalar(ar_s_H)-_se[ready_debt_kink_high]))
postclose `p_validate'
preserve
    use "`outdir'/nostate_estimator_validation.dta", clear
    export delimited using "`outdir'/nostate_estimator_validation.csv", replace
restore

* Main hinge identities and readiness-cutoff identity.
generate double __formula = readiness100*max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_debt_ns
generate double __diff = abs(debt_kink_low-__formula) if sample_debt_ns
quietly summarize __diff, meanonly
post `p_formula' ("main debt low hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = readiness100*max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_debt_ns
generate double __diff = abs(debt_kink_high-__formula) if sample_debt_ns
quietly summarize __diff, meanonly
post `p_formula' ("main debt high hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_ready_ns
generate double __diff = abs(ready_debt_kink_low-__formula) if sample_ready_ns
quietly summarize __diff, meanonly
post `p_formula' ("readiness debt-cutoff low hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_ready_ns
generate double __diff = abs(ready_debt_kink_high-__formula) if sample_ready_ns
quietly summarize __diff, meanonly
post `p_formula' ("readiness debt-cutoff high hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
post `p_formula' ("readiness cutoff equals debt cutoff") (0) (1e-12) (1)
postclose `p_formula'
preserve
    use "`outdir'/nostate_formula_checks.dta", clear
    export delimited using "`outdir'/nostate_formula_checks.csv", replace
restore

* RSS-minimum validation for every competing criterion.
tempname p_critvalidate
postfile `p_critvalidate' str12 criterion double recorded_cutoff profile_min_rss rss_at_recorded_cutoff abs_rss_diff N N_low N_high byte count_identity cutoff_row_exists passed using "`outdir'/criterion_cutoff_validation.dta", replace
foreach key of local criterion_keys {
    if "`key'"=="theta" local qlabel "theta"
    if "`key'"=="debt" local qlabel "b"
    if "`key'"=="ma" local qlabel "mA"
    if "`key'"=="ya" local qlabel "YA"
    if "`key'"=="bma" local qlabel "b*mA"
    preserve
        use "`outdir'/criterion_rss_profiles.dta", clear
        keep if criterion=="`qlabel'"
        quietly summarize rss, meanonly
        local minrss = r(min)
        quietly count if abs(cutoff-scalar(cutoff_`key'))<1e-10
        local exists = r(N)==1
        quietly summarize rss if abs(cutoff-scalar(cutoff_`key'))<1e-10, meanonly
        local chosenrss = r(mean)
        local countok = scalar(low_n_`key')+scalar(high_n_`key')==scalar(N_debt_ns)
        post `p_critvalidate' ("`qlabel'") (scalar(cutoff_`key')) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (scalar(N_debt_ns)) (scalar(low_n_`key')) (scalar(high_n_`key')) (`countok') (`exists') (`exists' & `countok' & abs(`chosenrss'-`minrss')<1e-8)
    restore
}
postclose `p_critvalidate'
preserve
    use "`outdir'/criterion_cutoff_validation.dta", clear
    export delimited using "`outdir'/criterion_cutoff_validation.csv", replace
restore

tempname p_cutvalidate
postfile `p_cutvalidate' str12 equation str16 cutoff_source double recorded_cutoff profile_min_rss rss_at_recorded_cutoff abs_rss_diff byte cutoff_row_exists passed using "`outdir'/nostate_cutoff_validation.dta", replace
preserve
    use "`outdir'/criterion_rss_profiles.dta", clear
    keep if criterion=="theta"
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_debt_ns))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_debt_ns))<1e-10, meanonly
    local chosenrss = r(mean)
restore
post `p_cutvalidate' ("debt") ("debt_full") (scalar(rss_min_cutoff_debt_ns)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
post `p_cutvalidate' ("ready_debt") ("debt_full") (scalar(rss_min_cutoff_debt_ns)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
postclose `p_cutvalidate'
preserve
    use "`outdir'/nostate_cutoff_validation.dta", clear
    export delimited using "`outdir'/nostate_cutoff_validation.csv", replace
restore

* Metadata and row-level reproducibility audit.
tempname p_meta
postfile `p_meta' str56 item double value using "`outdir'/nostate_run_metadata.dta", replace
post `p_meta' ("source_observations") (scalar(N_source))
post `p_meta' ("source_duplicate_rows") (scalar(N_duplicate_source))
post `p_meta' ("bad_b_it_ln_debt_mapping_rows") (scalar(bad_b_it_mapping_rows_ns))
post `p_meta' ("max_theta_ln_debt_reconstruction_diff") (scalar(max_theta_reconstruction_diff_ns))
post `p_meta' ("debt_sample_observations") (scalar(N_debt_ns))
post `p_meta' ("debt_sample_countries") (scalar(G_debt_ns))
post `p_meta' ("debt_sample_years") (scalar(T_debt_ns))
post `p_meta' ("debt_sample_first_year") (scalar(year_min_debt_ns))
post `p_meta' ("debt_sample_last_year") (scalar(year_max_debt_ns))
post `p_meta' ("ready_sample_observations") (scalar(N_ready_ns))
post `p_meta' ("ready_sample_countries") (scalar(G_ready_ns))
post `p_meta' ("ready_sample_years") (scalar(T_ready_ns))
post `p_meta' ("ready_sample_first_year") (scalar(year_min_ready_ns))
post `p_meta' ("ready_sample_last_year") (scalar(year_max_ready_ns))
post `p_meta' ("rss_min_cutoff_debt_theta") (scalar(rss_min_cutoff_debt_ns))
post `p_meta' ("ready_rss_at_debt_cutoff") (scalar(rss_ready_at_debt_cutoff_ns))
post `p_meta' ("outcome_horizon") (`horizon')
post `p_meta' ("competing_criterion_count") (5)
postclose `p_meta'
preserve
    use "`outdir'/nostate_run_metadata.dta", clear
    export delimited using "`outdir'/nostate_run_metadata.csv", replace
restore

preserve
    keep country_name iso3 country_id year b_outcome_year A_outcome_year sample_debt_ns sample_ready_ns debt_ns_missing_count ready_ns_missing_count b_outcome A_outcome interest_revenue readiness100 readiness_lag ln_debt vulnerability100 b_it_theta mA_hat spread_saving_component YA_hat ln_debt_mA_hat theta_hat_A theta_recomputed_ln_debt theta_reconstruction_diff b_it_mapping_diff growth ln_constantgdp debt_hinge_low_ns debt_hinge_high_ns debt_kink_low debt_kink_high ready_debt_hinge_low_ns ready_debt_hinge_high_ns ready_debt_kink_low ready_debt_kink_high
    sort iso3 year
    export delimited using "`outdir'/nostate_sample_audit.csv", replace
restore

preserve
    keep country_name iso3 country_id year b_outcome_year A_outcome_year b_outcome A_outcome readiness100 readiness_lag interest_revenue ln_debt vulnerability100 b_it_theta mA_hat spread_saving_component YA_hat ln_debt_mA_hat theta_hat_A theta_recomputed_ln_debt theta_reconstruction_diff b_it_mapping_diff growth ln_constantgdp inflation_cpi reserves tt sample_debt_ns sample_ready_ns debt_hinge_low_ns debt_hinge_high_ns debt_kink_low debt_kink_high ready_debt_hinge_low_ns ready_debt_hinge_high_ns ready_debt_kink_low ready_debt_kink_high
    sort iso3 year
    save "`outdir'/doomloop_nostate_panel.dta", replace
    export delimited using "`outdir'/doomloop_nostate_panel.csv", replace
restore

display as result "ANALYSIS COMPLETE NO-STATE"
display as result "Debt no-b sample: N=" scalar(N_debt_ns) ", countries=" scalar(G_debt_ns) ", years=" scalar(T_debt_ns) ", theta cutoff=" scalar(rss_min_cutoff_debt_ns)
display as result "Readiness-change sample: N=" scalar(N_ready_ns) ", countries=" scalar(G_ready_ns) ", years=" scalar(T_ready_ns) ", inherited cutoff=" scalar(rss_min_cutoff_debt_ns)
display as result "Competing criteria estimated: 5; shared debt sample N=" scalar(N_debt_ns)
log close nostatelog
