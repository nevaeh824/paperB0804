version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Single-crossing kink marginal-effect workflow.
* Inputs are read-only. The empirical theta panel is merged 1:1 to source-only
* debt and interest-revenue fields. All final estimates use country and year FE
* with observation-level Huber--White robust standard errors.
* -----------------------------------------------------------------------------

args project horizon
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0804"
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
log using "`outdir'/doomloop.log", text replace name(mainlog)

display as text "ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "SOURCE: `sourcefile'"
display as text "THETA INPUT: `thetafile'"
display as text "OUTCOME HORIZON: debt_gdp(t+`horizon'); readiness(t+`=`horizon'-1')"
display as text "CUTOFF POLICY: equation-specific RSS minimization on the full-control common sample; candidates are observed theta values from P10 to P90."

capture confirm file "`sourcefile'"
if _rc {
    display as error "Source CSV not found."
    log close mainlog
    exit 601
}
capture confirm file "`thetafile'"
if _rc {
    display as error "Empirical-theta panel not found. Run empirical_theta/run_workflow.ps1 first."
    log close mainlog
    exit 601
}

* Source-only fields needed by the two new equations.
import delimited using "`sourcefile'", clear varnames(1) case(preserve) encoding(UTF-8)
compress
count
scalar N_source = r(N)
duplicates tag iso3 year, generate(__dup_source)
quietly count if __dup_source>0
if r(N)>0 {
    display as error "Duplicate source country-year keys found."
    log close mainlog
    exit 459
}

* interest_revenue is the only source percentage field merged at this stage;
* all other rate/index variables already arrive ratio-scaled in the theta panel.
confirm variable interest_revenue
recast double interest_revenue
quietly summarize interest_revenue, meanonly
scalar __interest_source_min = r(min)
scalar __interest_source_max = r(max)
generate double __interest_source = interest_revenue
replace interest_revenue = interest_revenue/100
generate double __interest_scale_diff = abs(interest_revenue-__interest_source/100) if !missing(__interest_source)
quietly summarize __interest_scale_diff, meanonly
scalar __interest_max_diff = cond(r(N)>0,r(max),0)
quietly summarize interest_revenue, meanonly
tempname p_units
postfile `p_units' str32 variable double source_min source_max ratio_min ratio_max max_abs_scaling_diff byte passed using "`outdir'/unit_scaling_checks.dta", replace
post `p_units' ("interest_revenue") (scalar(__interest_source_min)) (scalar(__interest_source_max)) (r(min)) (r(max)) (scalar(__interest_max_diff)) (scalar(__interest_max_diff)<=1e-12)
postclose `p_units'
preserve
    use "`outdir'/unit_scaling_checks.dta", clear
    format source_min source_max ratio_min ratio_max max_abs_scaling_diff %21.15g
    export delimited using "`outdir'/unit_scaling_checks.csv", replace datafmt
restore
drop __interest_source __interest_scale_diff
keep iso3 year debt interest_revenue
tempfile source_extra
save `source_extra', replace

* The theta panel retains every source row and all baseline controls.
use "`thetafile'", clear
compress
isid iso3 year
count
scalar N_theta_panel = r(N)
merge 1:1 iso3 year using `source_extra', assert(match) nogen
isid iso3 year

* The generated index must use the baseline debt/GDP state, not the debt
* amount. Reconstruct theta before any cutoff search so stale or mis-mapped
* upstream inputs fail closed.
foreach v in debt_gdp b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A {
    capture confirm variable `v'
    if _rc {
        display as error "Required empirical-theta component missing: `v'"
        log close mainlog
        exit 111
    }
}
generate double theta_recomputed_debt_gdp = debt_gdp*mA_hat + TA_hat if !missing(debt_gdp,mA_hat,TA_hat)
generate double theta_reconstruction_diff = abs(theta_hat_A-theta_recomputed_debt_gdp) if !missing(theta_hat_A,theta_recomputed_debt_gdp)
generate double b_it_mapping_diff = abs(b_it_theta-debt_gdp) if !missing(b_it_theta,debt_gdp)
quietly summarize theta_reconstruction_diff, meanonly
scalar max_theta_reconstruction_diff = r(max)
quietly summarize b_it_mapping_diff, meanonly
scalar max_b_it_mapping_diff = r(max)
quietly count if b_it_theta!=debt_gdp
scalar bad_b_it_mapping_rows = r(N)
if scalar(max_theta_reconstruction_diff)>1e-10 | scalar(max_b_it_mapping_diff)>1e-10 | scalar(bad_b_it_mapping_rows)>0 {
    display as error "Theta input is not debt_gdp*mA_hat + TA_hat, or b_it is not debt_gdp."
    log close mainlog
    exit 459
}
label variable theta_recomputed_debt_gdp "debt_gdp*mA_hat + TA_hat recomputed in doomloop"
label variable theta_reconstruction_diff "Absolute theta reconstruction difference"
label variable b_it_mapping_diff "Absolute difference between b_it alias and debt_gdp"
xtset country_id year

* Exact panel timing. F., F2., and L. return missing across calendar gaps.
if `horizon'==1 generate double b_outcome = F.debt_gdp-debt_gdp if !missing(F.debt_gdp,debt_gdp)
if `horizon'==2 generate double b_outcome = F2.debt_gdp-debt_gdp if !missing(F2.debt_gdp,debt_gdp)
generate int b_outcome_year = year+`horizon' if !missing(b_outcome)
if `horizon'==1 generate double A_outcome = readiness100
if `horizon'==2 generate double A_outcome = F.readiness100
generate int A_outcome_year = year+`horizon'-1 if !missing(A_outcome)
generate double readiness_lag = L.readiness100

label variable b_outcome "Change in debt/GDP from t to t+h"
label variable A_outcome "Readiness A at t+h-1 from exact panel timing"
label variable readiness_lag "Readiness at t-1 from exact panel lag"

* No doomloop specification includes CurrentGDP, ConstantGDP, or either log.
local xcontrol wsdi_days
local macro_debt growth inflation_cpi
local macro_ready growth inflation_cpi
local external reserves tt
local controls_debt `macro_debt' `external'
local controls_ready `macro_ready' `external'
local full_controls_debt `xcontrol' `controls_debt'
local full_controls_ready `xcontrol' `controls_ready'

* Each equation has one ex-ante full-control sample. Nested specifications and
* every cutoff candidate use the same equation-specific observations.
local debt_required b_outcome readiness100 theta_hat_A debt_gdp `full_controls_debt'
local ready_required A_outcome interest_revenue theta_hat_A readiness_lag `full_controls_ready'
egen int debt_missing_count = rowmiss(`debt_required')
egen int ready_missing_count = rowmiss(`ready_required')
generate byte sample_debt = debt_missing_count==0
generate byte sample_ready = ready_missing_count==0
label variable sample_debt "Locked common sample for forward debt-level kink models"
label variable sample_ready "Locked common sample for readiness-level kink models"

quietly count if sample_debt
scalar N_debt = r(N)
quietly count if sample_ready
scalar N_ready = r(N)
egen byte tag_country_debt = tag(country_id) if sample_debt
egen byte tag_year_debt = tag(year) if sample_debt
egen byte tag_country_ready = tag(country_id) if sample_ready
egen byte tag_year_ready = tag(year) if sample_ready
quietly count if tag_country_debt==1
scalar G_debt = r(N)
quietly count if tag_year_debt==1
scalar T_debt = r(N)
quietly summarize year if sample_debt, meanonly
scalar year_min_debt = r(min)
scalar year_max_debt = r(max)
quietly count if tag_country_ready==1
scalar G_ready = r(N)
quietly count if tag_year_ready==1
scalar T_ready = r(N)
quietly summarize year if sample_ready, meanonly
scalar year_min_ready = r(min)
scalar year_max_ready = r(max)

* Duplicate audit after merge; no observation is deleted.
duplicates tag iso3 year, generate(duplicate_key)
quietly count if duplicate_key>0
scalar N_duplicate = r(N)
preserve
    keep if duplicate_key>0
    keep country_name iso3 year duplicate_key
    sort iso3 year
    export delimited using "`outdir'/duplicate_country_year.csv", replace
restore
if scalar(N_duplicate)>0 {
    display as error "Duplicate merged country-year keys found."
    log close mainlog
    exit 459
}

tempfile master
save `master', replace

* -----------------------------------------------------------------------------
* Descriptive statistics, variation, and missing-data attribution.
* -----------------------------------------------------------------------------
tempname p_desc
postfile `p_desc' str12 equation str32 variable double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/descriptive_stats.dta", replace
foreach eq in debt ready {
    local flag sample_`eq'
    if "`eq'"=="debt" local vars b_outcome theta_hat_A readiness100 debt_gdp wsdi_days growth inflation_cpi reserves tt
    if "`eq'"=="ready" local vars A_outcome theta_hat_A interest_revenue readiness_lag wsdi_days growth inflation_cpi reserves tt
    foreach v of local vars {
        quietly summarize `v' if `flag', detail
        post `p_desc' ("`eq'") ("`v'") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    }
}
postclose `p_desc'
preserve
    use "`outdir'/descriptive_stats.dta", clear
    export delimited using "`outdir'/descriptive_stats.csv", replace
restore

tempname p_var
postfile `p_var' str12 equation str32 variable double sd_overall sd_between sd_within ratio_within_overall str24 fe_identification using "`outdir'/variation.dta", replace
foreach eq in debt ready {
    local flag sample_`eq'
    if "`eq'"=="debt" local vars b_outcome theta_hat_A readiness100 debt_gdp `full_controls_debt'
    if "`eq'"=="ready" local vars A_outcome theta_hat_A interest_revenue readiness_lag `full_controls_ready'
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
    use "`outdir'/variation.dta", clear
    export delimited using "`outdir'/variation.csv", replace
restore

tempname p_miss
postfile `p_miss' str12 equation str32 variable double missing_total missing_rate exclusive_loss using "`outdir'/missing_loss.dta", replace
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
    use "`outdir'/missing_loss.dta", clear
    export delimited using "`outdir'/missing_loss.csv", replace
restore

* -----------------------------------------------------------------------------
* Equation-specific RSS-minimizing cutoffs. Candidate theta values are the
* observed values in the inclusive P10--P90 range of the locked sample. RSS is
* from the complete full-control TWFE equation; robust VCE does not alter RSS.
* -----------------------------------------------------------------------------

quietly summarize theta_hat_A if sample_debt, detail
scalar theta_debt_min = r(min)
scalar theta_debt_p1 = r(p1)
scalar theta_debt_p10 = r(p10)
scalar theta_debt_p25 = r(p25)
scalar theta_debt_p50 = r(p50)
scalar theta_debt_mean = r(mean)
scalar theta_debt_p75 = r(p75)
scalar theta_debt_p90 = r(p90)
scalar theta_debt_p99 = r(p99)
scalar theta_debt_max = r(max)

format theta_hat_A %21.15g
quietly levelsof theta_hat_A if sample_debt & theta_hat_A>=scalar(theta_debt_p10) & theta_hat_A<=scalar(theta_debt_p90), local(debt_candidates) clean
generate double __hL = .
generate double __hH = .
generate double __xL = .
generate double __xH = .
scalar rss_min_debt = .
scalar rss_min_cutoff_debt = .
scalar cutoff_candidates_debt = 0
scalar cutoff_low_n_debt = .
scalar cutoff_high_n_debt = .
tempname p_rss_debt
postfile `p_rss_debt' double cutoff rss N low_n high_n using "`outdir'/rss_profile_debt.dta", replace
foreach c of local debt_candidates {
    quietly count if sample_debt & theta_hat_A<`c'
    local low_n = r(N)
    quietly count if sample_debt & theta_hat_A>`c'
    local high_n = r(N)
    local minside = max(50,ceil(.10*scalar(N_debt)))
    if `low_n'>=`minside' & `high_n'>=`minside' {
        quietly replace __hL = max(`c'-theta_hat_A,0) if sample_debt
        quietly replace __hH = max(theta_hat_A-`c',0) if sample_debt
        quietly replace __xL = readiness100*__hL if sample_debt
        quietly replace __xH = readiness100*__hH if sample_debt
        quietly areg b_outcome __xL __xH debt_gdp `full_controls_debt' i.year if sample_debt, absorb(country_id)
        local rss = e(rss)
        post `p_rss_debt' (`c') (`rss') (e(N)) (`low_n') (`high_n')
        scalar cutoff_candidates_debt = scalar(cutoff_candidates_debt)+1
        if missing(scalar(rss_min_debt)) | `rss'<scalar(rss_min_debt) {
            scalar rss_min_debt = `rss'
            scalar rss_min_cutoff_debt = `c'
            scalar cutoff_low_n_debt = `low_n'
            scalar cutoff_high_n_debt = `high_n'
        }
    }
}
postclose `p_rss_debt'
drop __hL __hH __xL __xH
if missing(scalar(rss_min_cutoff_debt)) {
    display as error "Debt cutoff search returned no admissible candidate."
    log close mainlog
    exit 498
}
preserve
    use "`outdir'/rss_profile_debt.dta", clear
    sort cutoff
    export delimited using "`outdir'/rss_profile_debt.csv", replace
restore

quietly summarize theta_hat_A if sample_ready, detail
scalar theta_ready_min = r(min)
scalar theta_ready_p1 = r(p1)
scalar theta_ready_p10 = r(p10)
scalar theta_ready_p25 = r(p25)
scalar theta_ready_p50 = r(p50)
scalar theta_ready_mean = r(mean)
scalar theta_ready_p75 = r(p75)
scalar theta_ready_p90 = r(p90)
scalar theta_ready_p99 = r(p99)
scalar theta_ready_max = r(max)
quietly levelsof theta_hat_A if sample_ready & theta_hat_A>=scalar(theta_ready_p10) & theta_hat_A<=scalar(theta_ready_p90), local(ready_candidates) clean
generate double __hL = .
generate double __hH = .
generate double __xL = .
generate double __xH = .
scalar rss_min_ready = .
scalar rss_min_cutoff_ready = .
scalar cutoff_candidates_ready = 0
scalar cutoff_low_n_ready = .
scalar cutoff_high_n_ready = .
tempname p_rss_ready
postfile `p_rss_ready' double cutoff rss N low_n high_n using "`outdir'/rss_profile_ready.dta", replace
foreach c of local ready_candidates {
    quietly count if sample_ready & theta_hat_A<`c'
    local low_n = r(N)
    quietly count if sample_ready & theta_hat_A>`c'
    local high_n = r(N)
    local minside = max(50,ceil(.10*scalar(N_ready)))
    if `low_n'>=`minside' & `high_n'>=`minside' {
        quietly replace __hL = max(`c'-theta_hat_A,0) if sample_ready
        quietly replace __hH = max(theta_hat_A-`c',0) if sample_ready
        quietly replace __xL = interest_revenue*__hL if sample_ready
        quietly replace __xH = interest_revenue*__hH if sample_ready
        quietly areg A_outcome __xL __xH readiness_lag `full_controls_ready' i.year if sample_ready, absorb(country_id)
        local rss = e(rss)
        post `p_rss_ready' (`c') (`rss') (e(N)) (`low_n') (`high_n')
        scalar cutoff_candidates_ready = scalar(cutoff_candidates_ready)+1
        if missing(scalar(rss_min_ready)) | `rss'<scalar(rss_min_ready) {
            scalar rss_min_ready = `rss'
            scalar rss_min_cutoff_ready = `c'
            scalar cutoff_low_n_ready = `low_n'
            scalar cutoff_high_n_ready = `high_n'
        }
    }
}
postclose `p_rss_ready'
drop __hL __hH __xL __xH
if missing(scalar(rss_min_cutoff_ready)) {
    display as error "Readiness cutoff search returned no admissible candidate."
    log close mainlog
    exit 498
}
preserve
    use "`outdir'/rss_profile_ready.dta", clear
    sort cutoff
    export delimited using "`outdir'/rss_profile_ready.csv", replace
restore

display as result "Debt rss_min_cutoff = " scalar(rss_min_cutoff_debt) "; RSS = " scalar(rss_min_debt)
display as result "Readiness rss_min_cutoff = " scalar(rss_min_cutoff_ready) "; RSS = " scalar(rss_min_ready)

* Save cutoff summary.
tempname p_cutoff
postfile `p_cutoff' str12 equation double rss_min_cutoff rss candidate_count trim_low trim_high low_n high_n theta_min theta_max using "`outdir'/cutoffs.dta", replace
post `p_cutoff' ("debt") (scalar(rss_min_cutoff_debt)) (scalar(rss_min_debt)) (scalar(cutoff_candidates_debt)) (scalar(theta_debt_p10)) (scalar(theta_debt_p90)) (scalar(cutoff_low_n_debt)) (scalar(cutoff_high_n_debt)) (scalar(theta_debt_min)) (scalar(theta_debt_max))
post `p_cutoff' ("ready") (scalar(rss_min_cutoff_ready)) (scalar(rss_min_ready)) (scalar(cutoff_candidates_ready)) (scalar(theta_ready_p10)) (scalar(theta_ready_p90)) (scalar(cutoff_low_n_ready)) (scalar(cutoff_high_n_ready)) (scalar(theta_ready_min)) (scalar(theta_ready_max))
postclose `p_cutoff'
preserve
    use "`outdir'/cutoffs.dta", clear
    export delimited using "`outdir'/cutoffs.csv", replace
restore

* Final hinge bases and regressors at the full-control RSS-minimizing cutoffs.
generate double debt_hinge_low = max(scalar(rss_min_cutoff_debt)-theta_hat_A,0) if sample_debt
generate double debt_hinge_high = max(theta_hat_A-scalar(rss_min_cutoff_debt),0) if sample_debt
generate double debt_kink_low = readiness100*debt_hinge_low if sample_debt
generate double debt_kink_high = readiness100*debt_hinge_high if sample_debt

generate double ready_hinge_low = max(scalar(rss_min_cutoff_ready)-theta_hat_A,0) if sample_ready
generate double ready_hinge_high = max(theta_hat_A-scalar(rss_min_cutoff_ready),0) if sample_ready
generate double ready_kink_low = interest_revenue*ready_hinge_low if sample_ready
generate double ready_kink_high = interest_revenue*ready_hinge_high if sample_ready

* Alternative readiness specification: hold c at the RSS-minimizing cutoff
* selected by the corresponding full-control debt equation.
generate double ready_debt_hinge_low = max(scalar(rss_min_cutoff_debt)-theta_hat_A,0) if sample_ready
generate double ready_debt_hinge_high = max(theta_hat_A-scalar(rss_min_cutoff_debt),0) if sample_ready
generate double ready_debt_kink_low = interest_revenue*ready_debt_hinge_low if sample_ready
generate double ready_debt_kink_high = interest_revenue*ready_debt_hinge_high if sample_ready
quietly areg A_outcome ready_debt_kink_low ready_debt_kink_high readiness_lag `full_controls_ready' i.year if sample_ready, absorb(country_id)
scalar rss_ready_at_debt_cutoff = e(rss)

label variable debt_kink_low "A*(c-theta)+; debt equation"
label variable debt_kink_high "A*(theta-c)+; debt equation"
label variable ready_kink_low "FT*(c-theta)+; readiness equation"
label variable ready_kink_high "FT*(theta-c)+; readiness equation"
label variable ready_debt_kink_low "FT*(c_debt-theta)+; readiness equation"
label variable ready_debt_kink_high "FT*(theta-c_debt)+; readiness equation"

* Direct regression variables and their construction inputs, summarized on each
* locked sample immediately before estimation. Units are attached in the report.
tempname p_regdesc
postfile `p_regdesc' str24 specification str12 equation str32 variable str24 role double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/regression_descriptive_stats.dta", replace
foreach eq in debt ready ready_debt {
    local flag sample_`eq'
    if "`eq'"=="ready_debt" local flag sample_ready
    if "`eq'"=="debt" {
        local spec "debt_with_b"
        local depvars b_outcome
        local regressors debt_kink_low debt_kink_high debt_gdp wsdi_days growth inflation_cpi reserves tt
        local inputs readiness100 theta_hat_A
    }
    if "`eq'"=="ready" {
        local spec "ready_with_lag"
        local depvars A_outcome
        local regressors ready_kink_low ready_kink_high readiness_lag wsdi_days growth inflation_cpi reserves tt
        local inputs interest_revenue theta_hat_A
    }
    if "`eq'"=="ready_debt" {
        local spec "ready_debt_cutoff"
        local depvars A_outcome
        local regressors ready_debt_kink_low ready_debt_kink_high readiness_lag wsdi_days growth inflation_cpi reserves tt
        local inputs interest_revenue theta_hat_A
    }
    foreach v of local depvars {
        quietly summarize `v' if `flag', detail
        post `p_regdesc' ("`spec'") ("`eq'") ("`v'") ("dependent_variable") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
    }
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
    use "`outdir'/regression_descriptive_stats.dta", clear
    export delimited using "`outdir'/regression_descriptive_stats.csv", replace
restore

* -----------------------------------------------------------------------------
* Three nested specifications per equation. The cutoff is selected once from
* the full-control equation and held fixed in every displayed column.
* -----------------------------------------------------------------------------
tempname p_stats p_coef p_equation
postfile `p_stats' str24 model str12 equation double cutoff N countries years first_year last_year r2_within r2_overall df_r byte macro_controls external_controls using "`outdir'/model_stats.dta", replace
postfile `p_coef' str24 model str12 equation str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/model_coefficients.dta", replace
postfile `p_equation' str24 model str244 equation_text using "`outdir'/equations.dta", replace

local dm1 "D1_core"
local dr1 "debt_kink_low debt_kink_high debt_gdp `xcontrol'"
local dq1 "Delta b(t+h)=b(t+h)-b(t): FE_i + FE_t + kink terms + rho_b*b(t) + gamma_X*X + error"
local dmc1 0
local dec1 0
local dm2 "D2_macro"
local dr2 "debt_kink_low debt_kink_high debt_gdp `xcontrol' `macro_debt'"
local dq2 "D1 + growth + inflation; GDP controls excluded"
local dmc2 1
local dec2 0
local dm3 "D3_full"
local dr3 "debt_kink_low debt_kink_high debt_gdp `full_controls_debt'"
local dq3 "D2 + reserves + terms of trade"
local dmc3 1
local dec3 1

forvalues z=1/3 {
    local mid "`dm`z''"
    local rhs "`dr`z''"
    quietly xtreg b_outcome `rhs' i.year if sample_debt, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg b_outcome `rhs' i.year if sample_debt, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("debt") (scalar(rss_min_cutoff_debt)) (e(N)) (scalar(G_debt)) (scalar(T_debt)) (scalar(year_min_debt)) (scalar(year_max_debt)) (`r2w') (`r2o') (e(df_r)) (`dmc`z'') (`dec`z'')
    post `p_equation' ("`mid'") ("`dq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc {
            post `p_coef' ("`mid'") ("debt") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        }
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            post `p_coef' ("`mid'") ("debt") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}

local rm1 "R1_core"
local rr1 "ready_kink_low ready_kink_high readiness_lag `xcontrol'"
local rq1 "A(t+h-1) = FE_i + FE_t + kink terms + rho_A*A(t-1) + gamma_X*X + error"
local rmc1 0
local rec1 0
local rm2 "R2_macro"
local rr2 "ready_kink_low ready_kink_high readiness_lag `xcontrol' `macro_ready'"
local rq2 "R1 + growth + inflation; GDP controls excluded"
local rmc2 1
local rec2 0
local rm3 "R3_full"
local rr3 "ready_kink_low ready_kink_high readiness_lag `full_controls_ready'"
local rq3 "R2 + reserves + terms of trade"
local rmc3 1
local rec3 1

forvalues z=1/3 {
    local mid "`rm`z''"
    local rhs "`rr`z''"
    quietly xtreg A_outcome `rhs' i.year if sample_ready, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg A_outcome `rhs' i.year if sample_ready, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("ready") (scalar(rss_min_cutoff_ready)) (e(N)) (scalar(G_ready)) (scalar(T_ready)) (scalar(year_min_ready)) (scalar(year_max_ready)) (`r2w') (`r2o') (e(df_r)) (`rmc`z'') (`rec`z'')
    post `p_equation' ("`mid'") ("`rq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc {
            post `p_coef' ("`mid'") ("ready") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        }
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            post `p_coef' ("`mid'") ("ready") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}

local rdm1 "RD1_core"
local rdr1 "ready_debt_kink_low ready_debt_kink_high readiness_lag `xcontrol'"
local rdq1 "A(t+h-1) at the full-control debt-equation RSS cutoff"
local rdmc1 0
local rdec1 0
local rdm2 "RD2_macro"
local rdr2 "ready_debt_kink_low ready_debt_kink_high readiness_lag `xcontrol' `macro_ready'"
local rdq2 "RD1 + growth + inflation; GDP controls excluded"
local rdmc2 1
local rdec2 0
local rdm3 "RD3_full"
local rdr3 "ready_debt_kink_low ready_debt_kink_high readiness_lag `full_controls_ready'"
local rdq3 "RD2 + reserves + terms of trade"
local rdmc3 1
local rdec3 1

forvalues z=1/3 {
    local mid "`rdm`z''"
    local rhs "`rdr`z''"
    quietly xtreg A_outcome `rhs' i.year if sample_ready, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg A_outcome `rhs' i.year if sample_ready, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("ready_debt") (scalar(rss_min_cutoff_debt)) (e(N)) (scalar(G_ready)) (scalar(T_ready)) (scalar(year_min_ready)) (scalar(year_max_ready)) (`r2w') (`r2o') (e(df_r)) (`rdmc`z'') (`rdec`z'')
    post `p_equation' ("`mid'") ("`rdq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc {
            post `p_coef' ("`mid'") ("ready_debt") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        }
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
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* Wald tests and single-crossing sign diagnostics.
tempname p_wald p_key
postfile `p_wald' str24 model str80 hypothesis double F df_num df_den p using "`outdir'/wald_tests.dta", replace
postfile `p_key' str12 equation double cutoff coefficient_low coefficient_high effective_a effective_b product_ab byte opposite_sign using "`outdir'/key_results.dta", replace

estimates restore D3_full
quietly test debt_kink_low debt_kink_high
post `p_wald' ("D3_full") ("low- and high-branch coefficients jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro_debt'
post `p_wald' ("D3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("D3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls_debt'
post `p_wald' ("D3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar debt_beta_L = _b[debt_kink_low]
scalar debt_beta_H = _b[debt_kink_high]
scalar debt_se_L = _se[debt_kink_low]
scalar debt_se_H = _se[debt_kink_high]
scalar debt_df = e(df_r)
post `p_key' ("debt") (scalar(rss_min_cutoff_debt)) (scalar(debt_beta_L)) (scalar(debt_beta_H)) (scalar(debt_beta_L)) (scalar(debt_beta_H)) (scalar(debt_beta_L)*scalar(debt_beta_H)) (scalar(debt_beta_L)*scalar(debt_beta_H)<0)

estimates restore R3_full
quietly test ready_kink_low ready_kink_high
post `p_wald' ("R3_full") ("low- and high-branch coefficients jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro_ready'
post `p_wald' ("R3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("R3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls_ready'
post `p_wald' ("R3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar ready_delta_L = _b[ready_kink_low]
scalar ready_delta_H = _b[ready_kink_high]
scalar ready_se_L = _se[ready_kink_low]
scalar ready_se_H = _se[ready_kink_high]
scalar ready_df = e(df_r)
scalar ready_effective_a = scalar(ready_delta_L)
scalar ready_effective_b = scalar(ready_delta_H)
post `p_key' ("ready") (scalar(rss_min_cutoff_ready)) (scalar(ready_delta_L)) (scalar(ready_delta_H)) (scalar(ready_effective_a)) (scalar(ready_effective_b)) (scalar(ready_effective_a)*scalar(ready_effective_b)) (scalar(ready_effective_a)*scalar(ready_effective_b)<0)

estimates restore RD3_full
quietly test ready_debt_kink_low ready_debt_kink_high
post `p_wald' ("RD3_full") ("branches jointly zero; debt-equation cutoff") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro_ready'
post `p_wald' ("RD3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("RD3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls_ready'
post `p_wald' ("RD3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar ready_debt_delta_L = _b[ready_debt_kink_low]
scalar ready_debt_delta_H = _b[ready_debt_kink_high]
scalar ready_debt_se_L = _se[ready_debt_kink_low]
scalar ready_debt_se_H = _se[ready_debt_kink_high]
scalar ready_debt_df = e(df_r)
post `p_key' ("ready_debt") (scalar(rss_min_cutoff_debt)) (scalar(ready_debt_delta_L)) (scalar(ready_debt_delta_H)) (scalar(ready_debt_delta_L)) (scalar(ready_debt_delta_H)) (scalar(ready_debt_delta_L)*scalar(ready_debt_delta_H)) (scalar(ready_debt_delta_L)*scalar(ready_debt_delta_H)<0)

postclose `p_wald'
postclose `p_key'
foreach f in wald_tests key_results {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* Point estimates of m(theta;c). Debt is the derivative with respect to A;
* readiness is the derivative with respect to FT.
tempname p_me
postfile `p_me' str12 equation str16 estimand str12 point double theta cutoff marginal_effect se t p ci_low ci_high using "`outdir'/marginal_effects.dta", replace

estimates restore D3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_debt_p10)
    if "`point'"=="P25" local th = scalar(theta_debt_p25)
    if "`point'"=="P50" local th = scalar(theta_debt_p50)
    if "`point'"=="Mean" local th = scalar(theta_debt_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_debt)
    if "`point'"=="P75" local th = scalar(theta_debt_p75)
    if "`point'"=="P90" local th = scalar(theta_debt_p90)
    if abs(`th'-scalar(rss_min_cutoff_debt))<1e-12 {
        post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (0) (0) (.) (.) (0) (0)
    }
    else if `th'<scalar(rss_min_cutoff_debt) {
        local weight = scalar(rss_min_cutoff_debt)-`th'
        quietly lincom `weight'*debt_kink_low
        post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_debt)
        quietly lincom `weight'*debt_kink_high
        post `p_me' ("debt") ("dB/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}

estimates restore R3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_ready_p10)
    if "`point'"=="P25" local th = scalar(theta_ready_p25)
    if "`point'"=="P50" local th = scalar(theta_ready_p50)
    if "`point'"=="Mean" local th = scalar(theta_ready_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_ready)
    if "`point'"=="P75" local th = scalar(theta_ready_p75)
    if "`point'"=="P90" local th = scalar(theta_ready_p90)
    if abs(`th'-scalar(rss_min_cutoff_ready))<1e-12 {
        post `p_me' ("ready") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready)) (0) (0) (.) (.) (0) (0)
    }
    else if `th'<scalar(rss_min_cutoff_ready) {
        local weight = scalar(rss_min_cutoff_ready)-`th'
        quietly lincom `weight'*ready_kink_low
        post `p_me' ("ready") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_ready)
        quietly lincom `weight'*ready_kink_high
        post `p_me' ("ready") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}

estimates restore RD3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_ready_p10)
    if "`point'"=="P25" local th = scalar(theta_ready_p25)
    if "`point'"=="P50" local th = scalar(theta_ready_p50)
    if "`point'"=="Mean" local th = scalar(theta_ready_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_debt)
    if "`point'"=="P75" local th = scalar(theta_ready_p75)
    if "`point'"=="P90" local th = scalar(theta_ready_p90)
    if abs(`th'-scalar(rss_min_cutoff_debt))<1e-12 {
        post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (0) (0) (.) (.) (0) (0)
    }
    else if `th'<scalar(rss_min_cutoff_debt) {
        local weight = scalar(rss_min_cutoff_debt)-`th'
        quietly lincom `weight'*ready_debt_kink_low
        post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_debt)
        quietly lincom `weight'*ready_debt_kink_high
        post `p_me' ("ready_debt") ("dA/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_debt)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}
postclose `p_me'
preserve
    use "`outdir'/marginal_effects.dta", clear
    export delimited using "`outdir'/marginal_effects.csv", replace
restore

* -----------------------------------------------------------------------------
* Curve data and figures. P1--P99 avoids plotting a handful of extreme theta
* values while retaining the empirical cutoff and the central 98% of support.
* Pointwise confidence intervals condition on the selected cutoff and theta.
* -----------------------------------------------------------------------------
preserve
    clear
    set obs 202
    generate double theta = scalar(theta_debt_p1) + (_n-1)*(scalar(theta_debt_p99)-scalar(theta_debt_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_debt) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_debt)
    generate double marginal_effect = cond(theta<cutoff,scalar(debt_beta_L)*(cutoff-theta),scalar(debt_beta_H)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(debt_se_L),abs(theta-cutoff)*scalar(debt_se_H))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(debt_df),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/marginal_curve_debt.dta", replace
    export delimited using "`outdir'/marginal_curve_debt.csv", replace
    twoway ///
        (rarea ci_low ci_high theta, color("214 229 242")) ///
        (line marginal_effect theta, lcolor("31 119 180") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_debt)', lcolor(gs6) lpattern(dash) lwidth(medthin)) ///
        yline(0, lcolor(gs8) lpattern(solid) lwidth(thin)) ///
        title("Readiness effect on change in debt/GDP through t+`horizon'", color(black) size(medsmall)) ///
        subtitle("m(theta;c) from the full-control kink model; pointwise 95% CI; P1-P99 support", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ///
        ytitle("Marginal effect on change in debt/GDP", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) ///
        graphregion(color(white)) plotregion(color(white)) ///
        note("Positive values imply a larger debt/GDP increase; dashed line: debt-equation RSS cutoff.", size(vsmall) color(gs5)) ///
        name(g_debt, replace)
    graph export "`figuredir'/debt_marginal_effect.png", replace width(2400)
    graph export "`figuredir'/debt_marginal_effect.pdf", replace
restore

preserve
    clear
    set obs 202
    generate double theta = scalar(theta_ready_p1) + (_n-1)*(scalar(theta_ready_p99)-scalar(theta_ready_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_ready) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_ready)
    generate double marginal_effect = cond(theta<cutoff,scalar(ready_effective_a)*(cutoff-theta),scalar(ready_effective_b)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(ready_se_L),abs(theta-cutoff)*scalar(ready_se_H))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(ready_df),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/marginal_curve_ready.dta", replace
    export delimited using "`outdir'/marginal_curve_ready.csv", replace
    twoway ///
        (rarea ci_low ci_high theta, color("252 225 199")) ///
        (line marginal_effect theta, lcolor("230 100 10") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_ready)', lcolor(gs6) lpattern(dash) lwidth(medthin)) ///
        yline(0, lcolor(gs8) lpattern(solid) lwidth(thin)) ///
        title("Fiscal-pressure effect on readiness at t+`=`horizon'-1'", color(black) size(medsmall)) ///
        subtitle("dA/dFT at the readiness-equation RSS cutoff; pointwise 95% CI", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ///
        ytitle("Marginal effect on readiness level", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) ///
        graphregion(color(white)) plotregion(color(white)) ///
        note("Positive values imply higher readiness; dashed line: readiness-equation RSS cutoff.", size(vsmall) color(gs5)) ///
        name(g_ready, replace)
    graph export "`figuredir'/readiness_marginal_effect.png", replace width(2400)
    graph export "`figuredir'/readiness_marginal_effect.pdf", replace
restore

preserve
    clear
    set obs 202
    generate double theta = scalar(theta_ready_p1) + (_n-1)*(scalar(theta_ready_p99)-scalar(theta_ready_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_debt) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_debt)
    generate double marginal_effect = cond(theta<cutoff,scalar(ready_debt_delta_L)*(cutoff-theta),scalar(ready_debt_delta_H)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(ready_debt_se_L),abs(theta-cutoff)*scalar(ready_debt_se_H))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(ready_debt_df),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/marginal_curve_ready_debt_cutoff.dta", replace
    export delimited using "`outdir'/marginal_curve_ready_debt_cutoff.csv", replace
    twoway ///
        (rarea ci_low ci_high theta, color("226 239 218")) ///
        (line marginal_effect theta, lcolor("44 127 55") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_debt)', lcolor(gs6) lpattern(dash) lwidth(medthin)) ///
        yline(0, lcolor(gs8) lpattern(solid) lwidth(thin)) ///
        title("Readiness at debt-equation cutoff", color(black) size(medsmall)) ///
        subtitle("A at t+`=`horizon'-1'; pointwise 95% CI; P1-P99 support", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ///
        ytitle("Marginal effect on readiness level", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) ///
        graphregion(color(white)) plotregion(color(white)) ///
        note("Dashed line: cutoff minimizing RSS in the full-control debt equation.", size(vsmall) color(gs5)) ///
        name(g_ready_debt, replace)
    graph export "`figuredir'/readiness_marginal_effect_debt_cutoff.png", replace width(2400)
    graph export "`figuredir'/readiness_marginal_effect_debt_cutoff.pdf", replace
restore

graph combine g_debt g_ready g_ready_debt, cols(1) xcommon graphregion(color(white)) imargin(tiny) name(g_combined, replace)
graph export "`figuredir'/kink_marginal_effects.png", replace width(2400)
graph export "`figuredir'/kink_marginal_effects.pdf", replace

* -----------------------------------------------------------------------------
* Estimator equivalence: absorbed FE versus explicit country/year LSDV for the
* two preferred full-control equations, including robust standard errors.
* -----------------------------------------------------------------------------
tempname p_validate
postfile `p_validate' str12 equation str32 variable double areg_b lsdv_b abs_b_diff areg_se lsdv_se abs_se_diff using "`outdir'/estimator_validation.dta", replace

estimates restore D3_full
foreach v in debt_kink_low debt_kink_high debt_gdp `full_controls_debt' {
    scalar ar_b_`v' = _b[`v']
    scalar ar_s_`v' = _se[`v']
}
quietly regress b_outcome debt_kink_low debt_kink_high debt_gdp `full_controls_debt' i.country_id i.year if sample_debt, vce(robust)
foreach v in debt_kink_low debt_kink_high debt_gdp `full_controls_debt' {
    post `p_validate' ("debt") ("`v'") (scalar(ar_b_`v')) (_b[`v']) (abs(scalar(ar_b_`v')-_b[`v'])) (scalar(ar_s_`v')) (_se[`v']) (abs(scalar(ar_s_`v')-_se[`v']))
}

estimates restore R3_full
foreach v in ready_kink_low ready_kink_high readiness_lag `full_controls_ready' {
    scalar ar_b_`v' = _b[`v']
    scalar ar_s_`v' = _se[`v']
}
quietly regress A_outcome ready_kink_low ready_kink_high readiness_lag `full_controls_ready' i.country_id i.year if sample_ready, vce(robust)
foreach v in ready_kink_low ready_kink_high readiness_lag `full_controls_ready' {
    post `p_validate' ("ready") ("`v'") (scalar(ar_b_`v')) (_b[`v']) (abs(scalar(ar_b_`v')-_b[`v'])) (scalar(ar_s_`v')) (_se[`v']) (abs(scalar(ar_s_`v')-_se[`v']))
}

estimates restore RD3_full
foreach v in ready_debt_kink_low ready_debt_kink_high readiness_lag `full_controls_ready' {
    scalar ar_b_`v' = _b[`v']
    scalar ar_s_`v' = _se[`v']
}
quietly regress A_outcome ready_debt_kink_low ready_debt_kink_high readiness_lag `full_controls_ready' i.country_id i.year if sample_ready, vce(robust)
foreach v in ready_debt_kink_low ready_debt_kink_high readiness_lag `full_controls_ready' {
    post `p_validate' ("ready_debt") ("`v'") (scalar(ar_b_`v')) (_b[`v']) (abs(scalar(ar_b_`v')-_b[`v'])) (scalar(ar_s_`v')) (_se[`v']) (abs(scalar(ar_s_`v')-_se[`v']))
}
postclose `p_validate'
preserve
    use "`outdir'/estimator_validation.dta", clear
    export delimited using "`outdir'/estimator_validation.csv", replace
restore

* Formula checks in double precision.
tempname p_formula
postfile `p_formula' str48 check double max_abs_difference tolerance byte passed using "`outdir'/formula_checks.dta", replace
post `p_formula' ("theta uses debt_gdp*mA_hat + TA_hat") (scalar(max_theta_reconstruction_diff)) (1e-10) (scalar(max_theta_reconstruction_diff)<=1e-10)
post `p_formula' ("b_it maps exactly to debt_gdp") (scalar(max_b_it_mapping_diff)) (1e-10) (scalar(max_b_it_mapping_diff)<=1e-10 & scalar(bad_b_it_mapping_rows)==0)
if `horizon'==1 generate double __formula = F.debt_gdp-debt_gdp if !missing(b_outcome)
if `horizon'==2 generate double __formula = F2.debt_gdp-debt_gdp if !missing(b_outcome)
generate double __diff = abs(b_outcome-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("Delta b exact lead-minus-base formula") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
if `horizon'==1 generate double __formula = readiness100 if !missing(A_outcome)
if `horizon'==2 generate double __formula = F.readiness100 if !missing(A_outcome)
generate double __diff = abs(A_outcome-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("A outcome exact timing formula") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = readiness100*max(scalar(rss_min_cutoff_debt)-theta_hat_A,0) if sample_debt
generate double __diff = abs(debt_kink_low-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("debt low hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = readiness100*max(theta_hat_A-scalar(rss_min_cutoff_debt),0) if sample_debt
generate double __diff = abs(debt_kink_high-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("debt high hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(scalar(rss_min_cutoff_ready)-theta_hat_A,0) if sample_ready
generate double __diff = abs(ready_kink_low-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("readiness low hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(theta_hat_A-scalar(rss_min_cutoff_ready),0) if sample_ready
generate double __diff = abs(ready_kink_high-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("readiness high hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(scalar(rss_min_cutoff_debt)-theta_hat_A,0) if sample_ready
generate double __diff = abs(ready_debt_kink_low-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("readiness debt-cutoff low hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(theta_hat_A-scalar(rss_min_cutoff_debt),0) if sample_ready
generate double __diff = abs(ready_debt_kink_high-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("readiness debt-cutoff high hinge") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
postclose `p_formula'
preserve
    use "`outdir'/formula_checks.dta", clear
    export delimited using "`outdir'/formula_checks.csv", replace
restore

* Cutoff profiles must contain the recorded global minima.
tempname p_cutvalidate
postfile `p_cutvalidate' str12 equation double recorded_cutoff profile_min_rss rss_at_recorded_cutoff abs_rss_diff byte cutoff_row_exists passed using "`outdir'/cutoff_validation.dta", replace
preserve
    use "`outdir'/rss_profile_debt.dta", clear
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_debt))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_debt))<1e-10, meanonly
    local chosenrss = r(mean)
    post `p_cutvalidate' ("debt") (scalar(rss_min_cutoff_debt)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
restore
preserve
    use "`outdir'/rss_profile_ready.dta", clear
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_ready))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_ready))<1e-10, meanonly
    local chosenrss = r(mean)
    post `p_cutvalidate' ("ready") (scalar(rss_min_cutoff_ready)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
restore
preserve
    use "`outdir'/rss_profile_debt.dta", clear
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_debt))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_debt))<1e-10, meanonly
    local chosenrss = r(mean)
    post `p_cutvalidate' ("ready_debt") (scalar(rss_min_cutoff_debt)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
restore
postclose `p_cutvalidate'
preserve
    use "`outdir'/cutoff_validation.dta", clear
    export delimited using "`outdir'/cutoff_validation.csv", replace
restore

* Metadata, sample audit, and generated analysis panel.
quietly count if !missing(b_outcome) & b_outcome_year!=year+`horizon'
scalar bad_debt_year_alignment = r(N)
quietly count if !missing(A_outcome) & A_outcome_year!=year+`horizon'-1
scalar bad_ready_year_alignment = r(N)
quietly count if !missing(readiness_lag) & missing(L.readiness100)
scalar bad_readiness_lag_alignment = r(N)
quietly count if !missing(theta_hat_A)
scalar N_theta_constructible = r(N)

tempname p_meta
postfile `p_meta' str48 item double value using "`outdir'/run_metadata.dta", replace
post `p_meta' ("source_observations") (scalar(N_source))
post `p_meta' ("theta_panel_observations") (scalar(N_theta_panel))
post `p_meta' ("theta_constructible_observations") (scalar(N_theta_constructible))
post `p_meta' ("bad_b_it_debt_gdp_mapping_rows") (scalar(bad_b_it_mapping_rows))
post `p_meta' ("max_theta_debt_gdp_reconstruction_diff") (scalar(max_theta_reconstruction_diff))
post `p_meta' ("duplicate_rows") (scalar(N_duplicate))
post `p_meta' ("debt_sample_observations") (scalar(N_debt))
post `p_meta' ("debt_sample_countries") (scalar(G_debt))
post `p_meta' ("debt_sample_years") (scalar(T_debt))
post `p_meta' ("debt_sample_first_year") (scalar(year_min_debt))
post `p_meta' ("debt_sample_last_year") (scalar(year_max_debt))
post `p_meta' ("ready_sample_observations") (scalar(N_ready))
post `p_meta' ("ready_sample_countries") (scalar(G_ready))
post `p_meta' ("ready_sample_years") (scalar(T_ready))
post `p_meta' ("ready_sample_first_year") (scalar(year_min_ready))
post `p_meta' ("ready_sample_last_year") (scalar(year_max_ready))
post `p_meta' ("rss_min_cutoff_debt") (scalar(rss_min_cutoff_debt))
post `p_meta' ("rss_min_cutoff_ready") (scalar(rss_min_cutoff_ready))
post `p_meta' ("ready_rss_at_debt_cutoff") (scalar(rss_ready_at_debt_cutoff))
post `p_meta' ("outcome_horizon") (`horizon')
post `p_meta' ("bad_debt_year_alignment_rows") (scalar(bad_debt_year_alignment))
post `p_meta' ("bad_ready_year_alignment_rows") (scalar(bad_ready_year_alignment))
post `p_meta' ("bad_readiness_lag_alignment_rows") (scalar(bad_readiness_lag_alignment))
postclose `p_meta'
preserve
    use "`outdir'/run_metadata.dta", clear
    export delimited using "`outdir'/run_metadata.csv", replace
restore

preserve
    keep country_name iso3 country_id year b_outcome_year A_outcome_year duplicate_key sample_debt sample_ready debt_missing_count ready_missing_count b_outcome A_outcome debt_gdp wsdi_days b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A theta_recomputed_debt_gdp theta_reconstruction_diff b_it_mapping_diff debt_hinge_low debt_hinge_high debt_kink_low debt_kink_high ready_hinge_low ready_hinge_high ready_kink_low ready_kink_high ready_debt_hinge_low ready_debt_hinge_high ready_debt_kink_low ready_debt_kink_high
    sort iso3 year
    export delimited using "`outdir'/sample_audit.csv", replace
restore

preserve
    keep country_name iso3 country_id year b_outcome_year A_outcome_year b_outcome A_outcome readiness100 readiness_lag interest_revenue debt_gdp wsdi_days b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A theta_recomputed_debt_gdp theta_reconstruction_diff b_it_mapping_diff growth inflation_cpi reserves tt sample_debt sample_ready debt_hinge_low debt_hinge_high debt_kink_low debt_kink_high ready_hinge_low ready_hinge_high ready_kink_low ready_kink_high ready_debt_hinge_low ready_debt_hinge_high ready_debt_kink_low ready_debt_kink_high
    sort iso3 year
    save "`outdir'/doomloop_panel.dta", replace
    export delimited using "`outdir'/doomloop_panel.csv", replace
restore

display as result "ANALYSIS COMPLETE"
display as result "Debt sample: N=" scalar(N_debt) ", countries=" scalar(G_debt) ", years=" scalar(T_debt) ", cutoff=" scalar(rss_min_cutoff_debt)
display as result "Readiness sample: N=" scalar(N_ready) ", countries=" scalar(G_ready) ", years=" scalar(T_ready) ", cutoff=" scalar(rss_min_cutoff_ready)
log close mainlog
