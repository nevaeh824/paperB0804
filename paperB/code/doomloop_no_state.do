version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Re-estimation of the two kink equations after removing b_it from the debt
* equation and A_(t-1) from the readiness-change equation. Each reduced
* equation gets its own locked sample and new RSS-minimizing cutoff.
* -----------------------------------------------------------------------------

args project
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0804"
local workflowdir "`project'/doomloop"
local outdir "`workflowdir'/stata_outputs"
local figuredir "`workflowdir'/figures"
local inputfile "`outdir'/doomloop_panel.dta"

capture mkdir "`workflowdir'"
capture mkdir "`outdir'"
capture mkdir "`figuredir'"
capture log close _all
log using "`outdir'/doomloop_no_state.log", text replace name(nostatelog)

display as text "NO-STATE ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "INPUT: `inputfile'"
display as text "DEBT EQUATION: b_it removed. READINESS EQUATION: A_(t-1) removed."

capture confirm file "`inputfile'"
if _rc {
    display as error "Base doomloop panel missing. Run doomloop.do first."
    log close nostatelog
    exit 601
}

use "`inputfile'", clear
compress
isid iso3 year

* Recheck the upstream empirical-index identity before the reduced models use
* theta in their cutoff searches.
foreach v in debt CurrentGDP ln_currentgdp b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A theta_recomputed_debt_CurrentGDP theta_reconstruction_diff b_it_mapping_diff {
    capture confirm variable `v'
    if _rc {
        display as error "Required debt/CurrentGDP-based theta component missing: `v'"
        log close nostatelog
        exit 111
    }
}
quietly summarize theta_reconstruction_diff, meanonly
scalar max_theta_reconstruction_diff_ns = r(max)
quietly summarize b_it_mapping_diff, meanonly
scalar max_b_it_mapping_diff_ns = r(max)
quietly count if CurrentGDP>0 & !missing(debt,CurrentGDP) & (missing(b_it_theta) | abs(b_it_theta-debt/CurrentGDP)>1e-10)
scalar bad_b_it_mapping_rows_ns = r(N)
if scalar(max_theta_reconstruction_diff_ns)>1e-10 | scalar(max_b_it_mapping_diff_ns)>1e-10 | scalar(bad_b_it_mapping_rows_ns)>0 {
    display as error "Reduced workflow received theta not constructed with b_it=debt/CurrentGDP."
    log close nostatelog
    exit 459
}
xtset country_id year
count
scalar N_panel = r(N)

local xcontrol vulnerability100
local macro growth inflation_cpi
local external reserves tt
local controls `macro' `external'
local full_controls `xcontrol' `controls'
local ready_controls `full_controls' ln_currentgdp

* Reduced-model common samples. J_readiness already requires A_t and A_(t-1)
* for its construction, but A_(t-1) is not an explanatory variable here.
local debt_required delta_debt_lead readiness100 theta_hat_A `full_controls'
local ready_required J_readiness interest_revenue theta_hat_A `ready_controls'
egen int debt_ns_missing_count = rowmiss(`debt_required')
egen int ready_ns_missing_count = rowmiss(`ready_required')
generate byte sample_debt_ns = debt_ns_missing_count==0
generate byte sample_ready_ns = ready_ns_missing_count==0
label variable sample_debt_ns "Debt kink sample without b_it control"
label variable sample_ready_ns "Readiness kink sample without A_(t-1) control"

quietly count if sample_debt_ns
scalar N_debt_ns = r(N)
quietly count if sample_ready_ns
scalar N_ready_ns = r(N)
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

* Theta support points for cutoff search, marginal effects, and figures.
quietly summarize theta_hat_A if sample_debt_ns, detail
scalar theta_debt_ns_min = r(min)
scalar theta_debt_ns_p1 = r(p1)
scalar theta_debt_ns_p10 = r(p10)
scalar theta_debt_ns_p25 = r(p25)
scalar theta_debt_ns_p50 = r(p50)
scalar theta_debt_ns_mean = r(mean)
scalar theta_debt_ns_p75 = r(p75)
scalar theta_debt_ns_p90 = r(p90)
scalar theta_debt_ns_p99 = r(p99)
scalar theta_debt_ns_max = r(max)

quietly summarize theta_hat_A if sample_ready_ns, detail
scalar theta_ready_ns_min = r(min)
scalar theta_ready_ns_p1 = r(p1)
scalar theta_ready_ns_p10 = r(p10)
scalar theta_ready_ns_p25 = r(p25)
scalar theta_ready_ns_p50 = r(p50)
scalar theta_ready_ns_mean = r(mean)
scalar theta_ready_ns_p75 = r(p75)
scalar theta_ready_ns_p90 = r(p90)
scalar theta_ready_ns_p99 = r(p99)
scalar theta_ready_ns_max = r(max)

format theta_hat_A %21.15g

* -----------------------------------------------------------------------------
* New equation-specific RSS searches without the state controls.
* -----------------------------------------------------------------------------
quietly levelsof theta_hat_A if sample_debt_ns & theta_hat_A>=scalar(theta_debt_ns_p10) & theta_hat_A<=scalar(theta_debt_ns_p90), local(debt_candidates) clean
generate double __hL = .
generate double __hH = .
generate double __xL = .
generate double __xH = .
scalar rss_min_debt_ns = .
scalar rss_min_cutoff_debt_ns = .
scalar cutoff_candidates_debt_ns = 0
scalar cutoff_low_n_debt_ns = .
scalar cutoff_high_n_debt_ns = .
tempname p_rss_debt
postfile `p_rss_debt' double cutoff rss N low_n high_n using "`outdir'/nostate_rss_profile_debt.dta", replace
foreach c of local debt_candidates {
    quietly count if sample_debt_ns & theta_hat_A<`c'
    local low_n = r(N)
    quietly count if sample_debt_ns & theta_hat_A>`c'
    local high_n = r(N)
    local minside = max(50,ceil(.10*scalar(N_debt_ns)))
    if `low_n'>=`minside' & `high_n'>=`minside' {
        quietly replace __hL = max(`c'-theta_hat_A,0) if sample_debt_ns
        quietly replace __hH = max(theta_hat_A-`c',0) if sample_debt_ns
        quietly replace __xL = readiness100*__hL if sample_debt_ns
        quietly replace __xH = readiness100*__hH if sample_debt_ns
        quietly areg delta_debt_lead __xL __xH `full_controls' i.year if sample_debt_ns, absorb(country_id)
        local rss = e(rss)
        post `p_rss_debt' (`c') (`rss') (e(N)) (`low_n') (`high_n')
        scalar cutoff_candidates_debt_ns = scalar(cutoff_candidates_debt_ns)+1
        if missing(scalar(rss_min_debt_ns)) | `rss'<scalar(rss_min_debt_ns) {
            scalar rss_min_debt_ns = `rss'
            scalar rss_min_cutoff_debt_ns = `c'
            scalar cutoff_low_n_debt_ns = `low_n'
            scalar cutoff_high_n_debt_ns = `high_n'
        }
    }
}
postclose `p_rss_debt'
drop __hL __hH __xL __xH
if missing(scalar(rss_min_cutoff_debt_ns)) {
    display as error "No admissible debt cutoff without b_it."
    log close nostatelog
    exit 498
}
preserve
    use "`outdir'/nostate_rss_profile_debt.dta", clear
    sort cutoff
    export delimited using "`outdir'/nostate_rss_profile_debt.csv", replace
restore

quietly levelsof theta_hat_A if sample_ready_ns & theta_hat_A>=scalar(theta_ready_ns_p10) & theta_hat_A<=scalar(theta_ready_ns_p90), local(ready_candidates) clean
generate double __hL = .
generate double __hH = .
generate double __xL = .
generate double __xH = .
scalar rss_min_ready_ns = .
scalar rss_min_cutoff_ready_ns = .
scalar cutoff_candidates_ready_ns = 0
scalar cutoff_low_n_ready_ns = .
scalar cutoff_high_n_ready_ns = .
tempname p_rss_ready
postfile `p_rss_ready' double cutoff rss N low_n high_n using "`outdir'/nostate_rss_profile_ready.dta", replace
foreach c of local ready_candidates {
    quietly count if sample_ready_ns & theta_hat_A<`c'
    local low_n = r(N)
    quietly count if sample_ready_ns & theta_hat_A>`c'
    local high_n = r(N)
    local minside = max(50,ceil(.10*scalar(N_ready_ns)))
    if `low_n'>=`minside' & `high_n'>=`minside' {
        quietly replace __hL = max(`c'-theta_hat_A,0) if sample_ready_ns
        quietly replace __hH = max(theta_hat_A-`c',0) if sample_ready_ns
        quietly replace __xL = interest_revenue*__hL if sample_ready_ns
        quietly replace __xH = interest_revenue*__hH if sample_ready_ns
        quietly areg J_readiness __xL __xH `ready_controls' i.year if sample_ready_ns, absorb(country_id)
        local rss = e(rss)
        post `p_rss_ready' (`c') (`rss') (e(N)) (`low_n') (`high_n')
        scalar cutoff_candidates_ready_ns = scalar(cutoff_candidates_ready_ns)+1
        if missing(scalar(rss_min_ready_ns)) | `rss'<scalar(rss_min_ready_ns) {
            scalar rss_min_ready_ns = `rss'
            scalar rss_min_cutoff_ready_ns = `c'
            scalar cutoff_low_n_ready_ns = `low_n'
            scalar cutoff_high_n_ready_ns = `high_n'
        }
    }
}
postclose `p_rss_ready'
drop __hL __hH __xL __xH
if missing(scalar(rss_min_cutoff_ready_ns)) {
    display as error "No admissible readiness cutoff without A_(t-1)."
    log close nostatelog
    exit 498
}
preserve
    use "`outdir'/nostate_rss_profile_ready.dta", clear
    sort cutoff
    export delimited using "`outdir'/nostate_rss_profile_ready.csv", replace
restore

display as result "Debt no-b rss_min_cutoff = " scalar(rss_min_cutoff_debt_ns) "; RSS = " scalar(rss_min_debt_ns)
display as result "Readiness no-lag rss_min_cutoff = " scalar(rss_min_cutoff_ready_ns) "; RSS = " scalar(rss_min_ready_ns)

tempname p_cutoff
postfile `p_cutoff' str12 equation double rss_min_cutoff rss candidate_count trim_low trim_high low_n high_n theta_min theta_max using "`outdir'/nostate_cutoffs.dta", replace
post `p_cutoff' ("debt") (scalar(rss_min_cutoff_debt_ns)) (scalar(rss_min_debt_ns)) (scalar(cutoff_candidates_debt_ns)) (scalar(theta_debt_ns_p10)) (scalar(theta_debt_ns_p90)) (scalar(cutoff_low_n_debt_ns)) (scalar(cutoff_high_n_debt_ns)) (scalar(theta_debt_ns_min)) (scalar(theta_debt_ns_max))
post `p_cutoff' ("ready") (scalar(rss_min_cutoff_ready_ns)) (scalar(rss_min_ready_ns)) (scalar(cutoff_candidates_ready_ns)) (scalar(theta_ready_ns_p10)) (scalar(theta_ready_ns_p90)) (scalar(cutoff_low_n_ready_ns)) (scalar(cutoff_high_n_ready_ns)) (scalar(theta_ready_ns_min)) (scalar(theta_ready_ns_max))
postclose `p_cutoff'
preserve
    use "`outdir'/nostate_cutoffs.dta", clear
    export delimited using "`outdir'/nostate_cutoffs.csv", replace
restore

* Final reduced-model hinge regressors. The source panel retains the original
* kink variables, so replace them only in this reduced-model analysis copy.
capture drop debt_kink_low debt_kink_high ready_kink_low ready_kink_high
generate double debt_hinge_low_ns = max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_debt_ns
generate double debt_hinge_high_ns = max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_debt_ns
generate double debt_kink_low = readiness100*debt_hinge_low_ns if sample_debt_ns
generate double debt_kink_high = readiness100*debt_hinge_high_ns if sample_debt_ns
generate double ready_hinge_low_ns = max(scalar(rss_min_cutoff_ready_ns)-theta_hat_A,0) if sample_ready_ns
generate double ready_hinge_high_ns = max(theta_hat_A-scalar(rss_min_cutoff_ready_ns),0) if sample_ready_ns
generate double ready_kink_low = interest_revenue*ready_hinge_low_ns if sample_ready_ns
generate double ready_kink_high = interest_revenue*ready_hinge_high_ns if sample_ready_ns

* Direct reduced-model variables and construction inputs, summarized on the
* corresponding locked samples immediately before estimation.
tempname p_regdesc
postfile `p_regdesc' str24 specification str12 equation str32 variable str24 role double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/nostate_regression_descriptive_stats.dta", replace
foreach eq in debt ready {
    local flag sample_`eq'_ns
    if "`eq'"=="debt" {
        local spec "debt_no_b"
        local depvars delta_debt_lead
        local regressors debt_kink_low debt_kink_high vulnerability100 growth inflation_cpi reserves tt
        local inputs readiness100 theta_hat_A
    }
    if "`eq'"=="ready" {
        local spec "ready_no_lag"
        local depvars J_readiness
        local regressors ready_kink_low ready_kink_high vulnerability100 growth inflation_cpi reserves tt ln_currentgdp
        local inputs interest_revenue theta_hat_A readiness100
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
    use "`outdir'/nostate_regression_descriptive_stats.dta", clear
    export delimited using "`outdir'/nostate_regression_descriptive_stats.csv", replace
restore

* -----------------------------------------------------------------------------
* Three columns per reduced equation: core, macro, full controls.
* -----------------------------------------------------------------------------
tempname p_stats p_coef p_equation
postfile `p_stats' str24 model str12 equation double cutoff N countries years first_year last_year r2_within r2_overall df_r byte macro_controls external_controls using "`outdir'/nostate_model_stats.dta", replace
postfile `p_coef' str24 model str12 equation str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/nostate_model_coefficients.dta", replace
postfile `p_equation' str24 model str244 equation_text using "`outdir'/nostate_equations.dta", replace

local dm1 "DN1_core"
local dr1 "debt_kink_low debt_kink_high `xcontrol'"
local dq1 "DeltaDebt = FE_i + FE_t + kink terms + gamma_X*X + error; b_it removed"
local dmc1 0
local dec1 0
local dm2 "DN2_macro"
local dr2 "debt_kink_low debt_kink_high `xcontrol' `macro'"
local dq2 "DN1 + macro controls; b_it removed"
local dmc2 1
local dec2 0
local dm3 "DN3_full"
local dr3 "debt_kink_low debt_kink_high `full_controls'"
local dq3 "DN2 + external controls; b_it removed"
local dmc3 1
local dec3 1

forvalues z=1/3 {
    local mid "`dm`z''"
    local rhs "`dr`z''"
    quietly xtreg delta_debt_lead `rhs' i.year if sample_debt_ns, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg delta_debt_lead `rhs' i.year if sample_debt_ns, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("debt") (scalar(rss_min_cutoff_debt_ns)) (e(N)) (scalar(G_debt_ns)) (scalar(T_debt_ns)) (scalar(year_min_debt_ns)) (scalar(year_max_debt_ns)) (`r2w') (`r2o') (e(df_r)) (`dmc`z'') (`dec`z'')
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

local rm1 "RN1_core"
local rr1 "ready_kink_low ready_kink_high `xcontrol' ln_currentgdp"
local rq1 "J = FE_i + FE_t + kink terms + gamma_X*X + eta_G*ln(CurrentGDP) + error; A_lag removed"
local rmc1 0
local rec1 0
local rm2 "RN2_macro"
local rr2 "ready_kink_low ready_kink_high `xcontrol' `macro' ln_currentgdp"
local rq2 "RN1 + macro controls; ln(CurrentGDP) retained; A_lag removed"
local rmc2 1
local rec2 0
local rm3 "RN3_full"
local rr3 "ready_kink_low ready_kink_high `ready_controls'"
local rq3 "RN2 + external controls; ln(CurrentGDP) retained; A_lag removed"
local rmc3 1
local rec3 1

forvalues z=1/3 {
    local mid "`rm`z''"
    local rhs "`rr`z''"
    quietly xtreg J_readiness `rhs' i.year if sample_ready_ns, fe
    local r2w = e(r2_w)
    local r2o = e(r2_o)
    quietly areg J_readiness `rhs' i.year if sample_ready_ns, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_stats' ("`mid'") ("ready") (scalar(rss_min_cutoff_ready_ns)) (e(N)) (scalar(G_ready_ns)) (scalar(T_ready_ns)) (scalar(year_min_ready_ns)) (scalar(year_max_ready_ns)) (`r2w') (`r2o') (e(df_r)) (`rmc`z'') (`rec`z'')
    post `p_equation' ("`mid'") ("`rq`z''")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc post `p_coef' ("`mid'") ("ready") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            post `p_coef' ("`mid'") ("ready") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
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

* Wald tests, branch signs, and preferred coefficients.
tempname p_wald p_key
postfile `p_wald' str24 model str80 hypothesis double F df_num df_den p using "`outdir'/nostate_wald_tests.dta", replace
postfile `p_key' str12 equation double cutoff coefficient_low coefficient_high effective_a effective_b product_ab byte opposite_sign using "`outdir'/nostate_key_results.dta", replace

estimates restore DN3_full
quietly test debt_kink_low debt_kink_high
post `p_wald' ("DN3_full") ("low- and high-branch coefficients jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro'
post `p_wald' ("DN3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("DN3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls'
post `p_wald' ("DN3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar debt_beta_L_ns = _b[debt_kink_low]
scalar debt_beta_H_ns = _b[debt_kink_high]
scalar debt_se_L_ns = _se[debt_kink_low]
scalar debt_se_H_ns = _se[debt_kink_high]
scalar debt_df_ns = e(df_r)
post `p_key' ("debt") (scalar(rss_min_cutoff_debt_ns)) (scalar(debt_beta_L_ns)) (scalar(debt_beta_H_ns)) (scalar(debt_beta_L_ns)) (scalar(debt_beta_H_ns)) (scalar(debt_beta_L_ns)*scalar(debt_beta_H_ns)) (scalar(debt_beta_L_ns)*scalar(debt_beta_H_ns)<0)

estimates restore RN3_full
quietly test ready_kink_low ready_kink_high
post `p_wald' ("RN3_full") ("low- and high-branch coefficients jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `macro'
post `p_wald' ("RN3_full") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `external'
post `p_wald' ("RN3_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test `controls'
post `p_wald' ("RN3_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
scalar ready_delta_L_ns = _b[ready_kink_low]
scalar ready_delta_H_ns = _b[ready_kink_high]
scalar ready_se_L_ns = _se[ready_kink_low]
scalar ready_se_H_ns = _se[ready_kink_high]
scalar ready_df_ns = e(df_r)
post `p_key' ("ready") (scalar(rss_min_cutoff_ready_ns)) (scalar(ready_delta_L_ns)) (scalar(ready_delta_H_ns)) (scalar(ready_delta_L_ns)) (scalar(ready_delta_H_ns)) (scalar(ready_delta_L_ns)*scalar(ready_delta_H_ns)) (scalar(ready_delta_L_ns)*scalar(ready_delta_H_ns)<0)
postclose `p_wald'
postclose `p_key'
foreach f in wald_tests key_results {
    preserve
        use "`outdir'/nostate_`f'.dta", clear
        export delimited using "`outdir'/nostate_`f'.csv", replace
    restore
}

* Marginal effects at named theta points.
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
    if abs(`th'-scalar(rss_min_cutoff_debt_ns))<1e-12 post `p_me' ("debt") ("dDeltaDebt/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (0) (0) (.) (.) (0) (0)
    else if `th'<scalar(rss_min_cutoff_debt_ns) {
        local weight = scalar(rss_min_cutoff_debt_ns)-`th'
        quietly lincom `weight'*debt_kink_low
        post `p_me' ("debt") ("dDeltaDebt/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_debt_ns)
        quietly lincom `weight'*debt_kink_high
        post `p_me' ("debt") ("dDeltaDebt/dA") ("`point'") (`th') (scalar(rss_min_cutoff_debt_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}

estimates restore RN3_full
foreach point in P10 P25 P50 Mean Cutoff P75 P90 {
    if "`point'"=="P10" local th = scalar(theta_ready_ns_p10)
    if "`point'"=="P25" local th = scalar(theta_ready_ns_p25)
    if "`point'"=="P50" local th = scalar(theta_ready_ns_p50)
    if "`point'"=="Mean" local th = scalar(theta_ready_ns_mean)
    if "`point'"=="Cutoff" local th = scalar(rss_min_cutoff_ready_ns)
    if "`point'"=="P75" local th = scalar(theta_ready_ns_p75)
    if "`point'"=="P90" local th = scalar(theta_ready_ns_p90)
    if abs(`th'-scalar(rss_min_cutoff_ready_ns))<1e-12 post `p_me' ("ready") ("dJ/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready_ns)) (0) (0) (.) (.) (0) (0)
    else if `th'<scalar(rss_min_cutoff_ready_ns) {
        local weight = scalar(rss_min_cutoff_ready_ns)-`th'
        quietly lincom `weight'*ready_kink_low
        post `p_me' ("ready") ("dJ/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    else {
        local weight = `th'-scalar(rss_min_cutoff_ready_ns)
        quietly lincom `weight'*ready_kink_high
        post `p_me' ("ready") ("dJ/dFT") ("`point'") (`th') (scalar(rss_min_cutoff_ready_ns)) (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
}
postclose `p_me'
preserve
    use "`outdir'/nostate_marginal_effects.dta", clear
    export delimited using "`outdir'/nostate_marginal_effects.csv", replace
restore

* Curve data and new figures for the reduced equations.
preserve
    clear
    set obs 202
    generate double theta = scalar(theta_debt_ns_p1) + (_n-1)*(scalar(theta_debt_ns_p99)-scalar(theta_debt_ns_p1))/200 in 1/201
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
    twoway ///
        (rarea ci_low ci_high theta, color("214 229 242")) ///
        (line marginal_effect theta, lcolor("31 119 180") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_debt_ns)', lcolor(gs6) lpattern(dash) lwidth(medthin)) ///
        yline(0, lcolor(gs8) lpattern(solid) lwidth(thin)) ///
        title("Debt-change marginal effect without b{subscript:it}", color(black) size(medsmall)) ///
        subtitle("Full controls excluding current debt; pointwise 95% CI; P1-P99 support", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ///
        ytitle("Marginal effect on next-period debt-change ratio", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) ///
        graphregion(color(white)) plotregion(color(white)) ///
        note("Positive values imply higher next-period debt changes; dashed line: re-estimated cutoff c.", size(vsmall) color(gs5)) ///
        name(g_debt_ns, replace)
    graph export "`figuredir'/debt_marginal_effect_no_b.png", replace width(2400)
    graph export "`figuredir'/debt_marginal_effect_no_b.pdf", replace
restore

preserve
    clear
    set obs 202
    generate double theta = scalar(theta_ready_ns_p1) + (_n-1)*(scalar(theta_ready_ns_p99)-scalar(theta_ready_ns_p1))/200 in 1/201
    replace theta = scalar(rss_min_cutoff_ready_ns) in 202
    sort theta
    generate double cutoff = scalar(rss_min_cutoff_ready_ns)
    generate double marginal_effect = cond(theta<cutoff,scalar(ready_delta_L_ns)*(cutoff-theta),scalar(ready_delta_H_ns)*(theta-cutoff))
    replace marginal_effect = 0 if abs(theta-cutoff)<1e-12
    generate double se = cond(theta<cutoff,abs(cutoff-theta)*scalar(ready_se_L_ns),abs(theta-cutoff)*scalar(ready_se_H_ns))
    replace se = 0 if abs(theta-cutoff)<1e-12
    generate double critical = invttail(scalar(ready_df_ns),.025)
    generate double ci_low = marginal_effect-critical*se
    generate double ci_high = marginal_effect+critical*se
    generate str8 branch = cond(theta<cutoff,"low",cond(theta>cutoff,"high","cutoff"))
    order theta cutoff branch marginal_effect se ci_low ci_high
    save "`outdir'/nostate_marginal_curve_ready.dta", replace
    export delimited using "`outdir'/nostate_marginal_curve_ready.csv", replace
    twoway ///
        (rarea ci_low ci_high theta, color("252 225 199")) ///
        (line marginal_effect theta, lcolor("230 100 10") lwidth(medthick)), ///
        xline(`=scalar(rss_min_cutoff_ready_ns)', lcolor(gs6) lpattern(dash) lwidth(medthin)) ///
        yline(0, lcolor(gs8) lpattern(solid) lwidth(thin)) ///
        title("Fiscal-pressure effect without lagged readiness", color(black) size(medsmall)) ///
        subtitle("Full controls excluding A(t-1); pointwise 95% CI; P1-P99 support", color(gs5) size(small)) ///
        xtitle("Empirical adaptation index theta^A", size(small)) ///
        ytitle("Marginal effect on readiness change", size(small)) ///
        legend(order(2 "Point estimate" 1 "95% CI") rows(1) size(small)) ///
        graphregion(color(white)) plotregion(color(white)) ///
        note("Positive values imply higher readiness changes; dashed line: re-estimated cutoff c.", size(vsmall) color(gs5)) ///
        name(g_ready_ns, replace)
    graph export "`figuredir'/readiness_marginal_effect_no_lag.png", replace width(2400)
    graph export "`figuredir'/readiness_marginal_effect_no_lag.pdf", replace
restore

graph combine g_debt_ns g_ready_ns, cols(1) xcommon graphregion(color(white)) imargin(tiny) name(g_nostate, replace)
graph export "`figuredir'/kink_marginal_effects_no_state.png", replace width(2400)
graph export "`figuredir'/kink_marginal_effects_no_state.pdf", replace

* Estimator validation for both reduced full-control equations.
tempname p_validate
postfile `p_validate' str12 equation str32 variable double areg_b lsdv_b abs_b_diff areg_se lsdv_se abs_se_diff using "`outdir'/nostate_estimator_validation.dta", replace
estimates restore DN3_full
foreach v in debt_kink_low debt_kink_high `full_controls' {
    scalar ar_b_`v' = _b[`v']
    scalar ar_s_`v' = _se[`v']
}
quietly regress delta_debt_lead debt_kink_low debt_kink_high `full_controls' i.country_id i.year if sample_debt_ns, vce(robust)
foreach v in debt_kink_low debt_kink_high `full_controls' {
    post `p_validate' ("debt") ("`v'") (scalar(ar_b_`v')) (_b[`v']) (abs(scalar(ar_b_`v')-_b[`v'])) (scalar(ar_s_`v')) (_se[`v']) (abs(scalar(ar_s_`v')-_se[`v']))
}
estimates restore RN3_full
foreach v in ready_kink_low ready_kink_high `ready_controls' {
    scalar ar_b_`v' = _b[`v']
    scalar ar_s_`v' = _se[`v']
}
quietly regress J_readiness ready_kink_low ready_kink_high `ready_controls' i.country_id i.year if sample_ready_ns, vce(robust)
foreach v in ready_kink_low ready_kink_high `ready_controls' {
    post `p_validate' ("ready") ("`v'") (scalar(ar_b_`v')) (_b[`v']) (abs(scalar(ar_b_`v')-_b[`v'])) (scalar(ar_s_`v')) (_se[`v']) (abs(scalar(ar_s_`v')-_se[`v']))
}
postclose `p_validate'
preserve
    use "`outdir'/nostate_estimator_validation.dta", clear
    export delimited using "`outdir'/nostate_estimator_validation.csv", replace
restore

* Formula and RSS-minimum checks.
tempname p_formula
postfile `p_formula' str48 check double max_abs_difference tolerance byte passed using "`outdir'/nostate_formula_checks.dta", replace
post `p_formula' ("theta uses b_it*mA_hat + TA_hat") (scalar(max_theta_reconstruction_diff_ns)) (1e-10) (scalar(max_theta_reconstruction_diff_ns)<=1e-10)
post `p_formula' ("b_it maps to debt/CurrentGDP") (scalar(max_b_it_mapping_diff_ns)) (1e-10) (scalar(max_b_it_mapping_diff_ns)<=1e-10 & scalar(bad_b_it_mapping_rows_ns)==0)
generate double __formula = readiness100*max(scalar(rss_min_cutoff_debt_ns)-theta_hat_A,0) if sample_debt_ns
generate double __diff = abs(debt_kink_low-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("no-b debt low hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = readiness100*max(theta_hat_A-scalar(rss_min_cutoff_debt_ns),0) if sample_debt_ns
generate double __diff = abs(debt_kink_high-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("no-b debt high hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(scalar(rss_min_cutoff_ready_ns)-theta_hat_A,0) if sample_ready_ns
generate double __diff = abs(ready_kink_low-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("no-lag readiness low hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
generate double __formula = interest_revenue*max(theta_hat_A-scalar(rss_min_cutoff_ready_ns),0) if sample_ready_ns
generate double __diff = abs(ready_kink_high-__formula)
quietly summarize __diff, meanonly
post `p_formula' ("no-lag readiness high hinge regressor") (r(max)) (1e-10) (r(max)<=1e-10)
drop __formula __diff
postclose `p_formula'
preserve
    use "`outdir'/nostate_formula_checks.dta", clear
    export delimited using "`outdir'/nostate_formula_checks.csv", replace
restore

tempname p_cutvalidate
postfile `p_cutvalidate' str12 equation double recorded_cutoff profile_min_rss rss_at_recorded_cutoff abs_rss_diff byte cutoff_row_exists passed using "`outdir'/nostate_cutoff_validation.dta", replace
preserve
    use "`outdir'/nostate_rss_profile_debt.dta", clear
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_debt_ns))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_debt_ns))<1e-10, meanonly
    local chosenrss = r(mean)
    post `p_cutvalidate' ("debt") (scalar(rss_min_cutoff_debt_ns)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
restore
preserve
    use "`outdir'/nostate_rss_profile_ready.dta", clear
    quietly summarize rss, meanonly
    local minrss = r(min)
    quietly count if abs(cutoff-scalar(rss_min_cutoff_ready_ns))<1e-10
    local exists = r(N)==1
    quietly summarize rss if abs(cutoff-scalar(rss_min_cutoff_ready_ns))<1e-10, meanonly
    local chosenrss = r(mean)
    post `p_cutvalidate' ("ready") (scalar(rss_min_cutoff_ready_ns)) (`minrss') (`chosenrss') (abs(`chosenrss'-`minrss')) (`exists') (`exists' & abs(`chosenrss'-`minrss')<1e-8)
restore
postclose `p_cutvalidate'
preserve
    use "`outdir'/nostate_cutoff_validation.dta", clear
    export delimited using "`outdir'/nostate_cutoff_validation.csv", replace
restore

* Metadata and row-level audit.
tempname p_meta
postfile `p_meta' str48 item double value using "`outdir'/nostate_run_metadata.dta", replace
post `p_meta' ("panel_observations") (scalar(N_panel))
post `p_meta' ("bad_b_it_debt_CurrentGDP_mapping_rows") (scalar(bad_b_it_mapping_rows_ns))
post `p_meta' ("max_theta_b_it_reconstruction_diff") (scalar(max_theta_reconstruction_diff_ns))
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
post `p_meta' ("rss_min_cutoff_debt") (scalar(rss_min_cutoff_debt_ns))
post `p_meta' ("rss_min_cutoff_ready") (scalar(rss_min_cutoff_ready_ns))
postclose `p_meta'
preserve
    use "`outdir'/nostate_run_metadata.dta", clear
    export delimited using "`outdir'/nostate_run_metadata.csv", replace
restore

preserve
    keep country_name iso3 country_id year sample_debt_ns sample_ready_ns debt_ns_missing_count ready_ns_missing_count debt CurrentGDP ln_currentgdp delta_debt_lead J_readiness debt_gdp vulnerability100 b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A theta_recomputed_debt_CurrentGDP theta_reconstruction_diff b_it_mapping_diff debt_hinge_low_ns debt_hinge_high_ns debt_kink_low debt_kink_high ready_hinge_low_ns ready_hinge_high_ns ready_kink_low ready_kink_high
    format debt CurrentGDP b_it_theta %21.15g
    sort iso3 year
    export delimited using "`outdir'/nostate_sample_audit.csv", replace datafmt
restore

preserve
    keep country_name iso3 country_id year debt debt_lead CurrentGDP ln_currentgdp delta_debt_lead readiness100 readiness_lag J_readiness interest_revenue debt_gdp vulnerability100 b_it_theta mA_hat spread_saving_component TA_hat theta_hat_A theta_recomputed_debt_CurrentGDP theta_reconstruction_diff b_it_mapping_diff growth inflation_cpi reserves tt sample_debt_ns sample_ready_ns debt_hinge_low_ns debt_hinge_high_ns debt_kink_low debt_kink_high ready_hinge_low_ns ready_hinge_high_ns ready_kink_low ready_kink_high
    format debt CurrentGDP b_it_theta %21.15g
    sort iso3 year
    save "`outdir'/doomloop_nostate_panel.dta", replace
    export delimited using "`outdir'/doomloop_nostate_panel.csv", replace datafmt
restore

display as result "ANALYSIS COMPLETE NO-STATE"
display as result "Debt no-b sample: N=" scalar(N_debt_ns) ", countries=" scalar(G_debt_ns) ", years=" scalar(T_debt_ns) ", cutoff=" scalar(rss_min_cutoff_debt_ns)
display as result "Readiness no-lag sample: N=" scalar(N_ready_ns) ", countries=" scalar(G_ready_ns) ", years=" scalar(T_ready_ns) ", cutoff=" scalar(rss_min_cutoff_ready_ns)
log close nostatelog
