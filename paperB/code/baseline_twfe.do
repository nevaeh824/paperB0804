version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Reproducible baseline TWFE analysis for invest_panel_weo.csv
* Original CSV is never overwritten. No observation is deleted from the master.
* All nested models use one ex-ante common sample.
* Standard errors use observation-level heteroskedasticity-robust VCE.
* Important: xtreg, fe vce(robust) clusters on the panel variable in Stata;
* therefore estimation uses areg, absorb(country_id) vce(robust), with year FE.
* -----------------------------------------------------------------------------

args project
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0804"
local datadir "`project'/data0804"
local workflowdir "`project'/baseline"
local outdir  "`workflowdir'/stata_outputs"
capture mkdir "`workflowdir'"
capture mkdir "`outdir'"
capture log close _all
log using "`outdir'/baseline_twfe.log", text replace name(mainlog)

display as text "ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "SOURCE: `datadir'/invest_panel_weo.csv"
display as text "POLICY: original data preserved; no silent deletion; common sample fixed before regressions."

import delimited using "`datadir'/invest_panel_weo.csv", clear varnames(1) case(preserve) encoding(UTF-8)
compress
count
scalar N_raw = r(N)

* Unified regression-unit convention: every rate, percentage, or 0--100 index
* used by the empirical workflow is represented as a 0--1 ratio. GDP amounts
* and their logarithms remain in the source scale. Source variable names are
* retained for cross-stage compatibility; the source CSV itself is read-only.
tempname p_units
postfile `p_units' str32 variable double source_min source_max ratio_min ratio_max max_abs_scaling_diff byte passed using "`outdir'/unit_scaling_checks.dta", replace
local ratio_vars bond_spreads bond_10y vulnerability100 readiness100 growth inflation_cpi debt_gdp PrimaryBalance_gdp reserves tt Revenue_gdp OverallBalance_gdp interest_revenue
foreach v of local ratio_vars {
    recast double `v'
    quietly summarize `v', meanonly
    local source_min = r(min)
    local source_max = r(max)
    generate double __source_value = `v'
    replace `v' = `v'/100
    generate double __scale_diff = abs(`v'-__source_value/100) if !missing(__source_value)
    quietly summarize __scale_diff, meanonly
    local scale_diff = r(max)
    quietly summarize `v', meanonly
    post `p_units' ("`v'") (`source_min') (`source_max') (r(min)) (r(max)) (`scale_diff') (`scale_diff'<=1e-12)
    drop __source_value __scale_diff
}
postclose `p_units'
preserve
    use "`outdir'/unit_scaling_checks.dta", clear
    format source_min source_max ratio_min ratio_max max_abs_scaling_diff %21.15g
    export delimited using "`outdir'/unit_scaling_checks.csv", replace datafmt
restore

label variable bond_spreads "Sovereign spread ratio; source percentage divided by 100"
label variable bond_10y "Ten-year yield ratio; source percentage divided by 100"
label variable vulnerability100 "ND-GAIN vulnerability ratio; source 0-100 index divided by 100"
label variable readiness100 "ND-GAIN readiness ratio; source 0-100 index divided by 100"
label variable debt_gdp "Government debt/GDP ratio; source percentage divided by 100"
label variable growth "Real GDP growth ratio; source percentage divided by 100"
label variable inflation_cpi "CPI inflation ratio; source percentage divided by 100"
label variable reserves "Reserves ratio; source value divided by 100"
label variable tt "Terms-of-trade ratio relative to 2015; source index divided by 100"
ds, has(type numeric)
local raw_numeric `r(varlist)'

* Stable numeric country identifier; original country variables are retained.
egen long country_id = group(iso3), label
label variable country_id "Numeric country identifier generated from iso3"

* Log controls and theoretical debt state, preserving source amounts.
confirm variable ConstantGDP
confirm variable debt
count if ConstantGDP<=0 & !missing(ConstantGDP)
scalar N_nonpositive_constant_gdp = r(N)
count if debt<=0 & !missing(debt)
scalar N_nonpositive_debt = r(N)
generate double ln_constantgdp = ln(ConstantGDP) if ConstantGDP>0
generate double ln_debt = ln(debt) if debt>0
label variable ln_constantgdp "Natural log of ConstantGDP; generated only when ConstantGDP>0"
label variable ln_debt "Natural log of government debt; generated only when debt>0"

* Panel-key uniqueness. Duplicates are exported and never deleted.
duplicates tag iso3 year, generate(duplicate_key)
quietly count if duplicate_key>0
scalar N_duplicate_rows = r(N)
preserve
    keep if duplicate_key>0
    keep country_name iso3 year duplicate_key
    sort iso3 year
    export delimited using "`outdir'/duplicate_country_year.csv", replace
restore
display as text "Duplicate country-year rows: " N_duplicate_rows

if scalar(N_duplicate_rows)>0 {
    display as error "Duplicate country-year keys exist. No rows were deleted. Regression workflow stopped."
    log close mainlog
    exit 459
}

xtset country_id year

* Exact model mapping.
local y        bond_spreads
local core     vulnerability100 readiness100 ln_debt
local always   growth ln_constantgdp
local macro    inflation_cpi
local external reserves tt
local controls `always' `macro' `external'
local modelvars `y' `core' `controls'

* One common sample for every reported regression.
egen int model_missing_count = rowmiss(`modelvars')
generate byte sample_common = (model_missing_count==0)
label variable sample_common "Common nonmissing sample for all baseline models"
quietly count if sample_common
scalar N_common = r(N)
quietly count if !sample_common
scalar N_common_lost = r(N)
egen byte tag_country_common = tag(country_id) if sample_common
egen byte tag_year_common = tag(year) if sample_common
quietly count if tag_country_common==1
scalar G_common = r(N)
quietly count if tag_year_common==1
scalar T_common = r(N)
quietly summarize year if sample_common, meanonly
scalar year_min_common = r(min)
scalar year_max_common = r(max)

tempfile master
save `master', replace

* -----------------------------------------------------------------------------
* Data profile: N, missing rate, moments and quantiles for every numeric source
* variable plus the generated log GDP variable.
* -----------------------------------------------------------------------------
local profilevars `raw_numeric' ln_constantgdp ln_debt
tempname p_profile
postfile `p_profile' str32 variable double N missing missing_rate mean sd min p10 p25 p50 p75 p90 max using "`outdir'/profile.dta", replace
foreach v of local profilevars {
    quietly count if !missing(`v')
    local n = r(N)
    quietly count if missing(`v')
    local m = r(N)
    local mr = 100*`m'/scalar(N_raw)
    quietly summarize `v', detail
    post `p_profile' ("`v'") (`n') (`m') (`mr') (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
postclose `p_profile'
preserve
    use "`outdir'/profile.dta", clear
    export delimited using "`outdir'/profile.csv", replace
restore

* Overall, between and within standard deviations.
tempname p_var
postfile `p_var' str32 variable double sd_overall sd_between sd_within ratio_within_overall str24 fe_identification using "`outdir'/variation.dta", replace
foreach v of local profilevars {
    quietly xtsum `v'
    local sdo = r(sd)
    local sdb = r(sd_b)
    local sdw = r(sd_w)
    local ratio = cond(`sdo'>0, `sdw'/`sdo', .)
    local ident "adequate"
    if missing(`sdw') | `sdw' <= 1e-10*max(1,`sdo') local ident "not_identified_by_FE"
    else if `ratio' < .01 local ident "low_within_variation"
    post `p_var' ("`v'") (`sdo') (`sdb') (`sdw') (`ratio') ("`ident'")
}
postclose `p_var'
preserve
    use "`outdir'/variation.dta", clear
    export delimited using "`outdir'/variation.csv", replace
restore

* Exact absorption checks. Threshold: residual SD <= 1e-10*max(1, overall SD).
tempname p_absorb
postfile `p_absorb' str32 variable byte country_absorbed time_absorbed twfe_absorbed double residual_sd tolerance using "`outdir'/absorption.dta", replace
foreach v of local profilevars {
    capture drop __sd_i __sd_t __twres
    bysort country_id: egen double __sd_i = sd(`v')
    quietly summarize __sd_i, meanonly
    local maxsdi = cond(missing(r(max)),0,r(max))
    bysort year: egen double __sd_t = sd(`v')
    quietly summarize __sd_t, meanonly
    local maxsdt = cond(missing(r(max)),0,r(max))
    quietly summarize `v'
    local tol = 1e-10*max(1,r(sd))
    quietly regress `v' i.country_id i.year if !missing(`v')
    predict double __twres if e(sample), residuals
    quietly summarize __twres
    local rsd = cond(missing(r(sd)),0,r(sd))
    local ca = (`maxsdi'<=`tol')
    local ta = (`maxsdt'<=`tol')
    local tw = (`rsd'<=`tol')
    post `p_absorb' ("`v'") (`ca') (`ta') (`tw') (`rsd') (`tol')
}
postclose `p_absorb'
capture drop __sd_i __sd_t __twres
preserve
    use "`outdir'/absorption.dta", clear
    export delimited using "`outdir'/absorption.csv", replace
restore

* Missing-data losses for every model variable: total missing and exclusive loss.
tempname p_miss
postfile `p_miss' str32 variable double missing_total missing_rate exclusive_loss using "`outdir'/missing_loss.dta", replace
foreach v of local modelvars {
    local others : list modelvars - v
    quietly count if missing(`v')
    local mt = r(N)
    capture drop __other_missing
    egen int __other_missing = rowmiss(`others')
    quietly count if missing(`v') & __other_missing==0
    local ex = r(N)
    post `p_miss' ("`v'") (`mt') (100*`mt'/scalar(N_raw)) (`ex')
}
capture drop __other_missing
postclose `p_miss'
preserve
    use "`outdir'/missing_loss.dta", clear
    export delimited using "`outdir'/missing_loss.csv", replace
restore

* Correlation matrix on the common sample.
quietly correlate `core' `controls' if sample_common
matrix CORR = r(C)
local corrvars `core' `controls'
tempname p_corr
postfile `p_corr' str32 variable_i str32 variable_j double correlation using "`outdir'/correlations.dta", replace
local i = 0
foreach vi of local corrvars {
    local ++i
    local j = 0
    foreach vj of local corrvars {
        local ++j
        post `p_corr' ("`vi'") ("`vj'") (CORR[`i',`j'])
    }
}
postclose `p_corr'
preserve
    use "`outdir'/correlations.dta", clear
    export delimited using "`outdir'/correlations.csv", replace
restore

* TWFE residualization followed by VIF and a correlation-matrix condition index.
local xvars `core' `controls'
local residuals
foreach v of local xvars {
    quietly regress `v' i.country_id i.year if sample_common
    predict double tw_`v' if sample_common, residuals
    local residuals `residuals' tw_`v'
}
quietly correlate `residuals' if sample_common
matrix RTW = r(C)
mata: st_numscalar("condition_number", sqrt(cond(st_matrix("RTW"))))
tempname p_vif
postfile `p_vif' str32 variable double vif tolerance condition_number using "`outdir'/collinearity.dta", replace
local k : word count `xvars'
forvalues j=1/`k' {
    local v  : word `j' of `xvars'
    local rv : word `j' of `residuals'
    local other_r : list residuals - rv
    quietly regress `rv' `other_r' if sample_common
    local vif = 1/(1-e(r2))
    post `p_vif' ("`v'") (`vif') (1/`vif') (scalar(condition_number))
}
postclose `p_vif'
preserve
    use "`outdir'/collinearity.dta", clear
    export delimited using "`outdir'/collinearity.csv", replace
restore

* Center interacting variables using common-sample means. Raw variables remain.
tempname p_center
postfile `p_center' str32 variable double mean sd min p10 p25 p50 p75 p90 max using "`outdir'/centering.dta", replace
foreach v in readiness100 ln_debt vulnerability100 {
    quietly summarize `v' if sample_common, detail
    scalar mean_`v' = r(mean)
    scalar sd_`v' = r(sd)
    scalar min_`v' = r(min)
    scalar max_`v' = r(max)
    scalar p10_`v' = r(p10)
    scalar p25_`v' = r(p25)
    scalar p50_`v' = r(p50)
    scalar p75_`v' = r(p75)
    scalar p90_`v' = r(p90)
    post `p_center' ("`v'") (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
postclose `p_center'
generate double c_A = readiness100 - scalar(mean_readiness100)
generate double c_b = ln_debt - scalar(mean_ln_debt)
generate double c_X = vulnerability100 - scalar(mean_vulnerability100)
generate double int_AB = c_A*c_b
generate double int_AX = c_A*c_X
label variable c_A "Mean-centered readiness100"
label variable c_b "Mean-centered ln_debt"
label variable c_X "Mean-centered vulnerability100"
label variable int_AB "c_A x c_b"
label variable int_AX "c_A x c_X"
preserve
    use "`outdir'/centering.dta", clear
    export delimited using "`outdir'/centering.csv", replace
restore

* -----------------------------------------------------------------------------
* TWFE regressions. All models use sample_common and observation-level robust SEs.
* areg supplies coefficients/inference; xtreg without robust VCE supplies the
* requested within and overall R-squared statistics for the identical model.
* C-Macro is the progressive macro-control step. No extra fiscal-control step is
* invented because ln_debt is already a core theoretical regressor and the user
* did not specify an additional fiscal control. Layer-2 is the all-controls step.
* -----------------------------------------------------------------------------
local m1  "A_X_only"
local r1  "vulnerability100 `always'"
local q1  "s_it = alpha_i + lambda_t + beta_X X_it + epsilon_it"
local m2  "A_A_only"
local r2  "readiness100 `always'"
local q2  "s_it = alpha_i + lambda_t + beta_A A_it + epsilon_it"
local m3  "A_b_only"
local r3  "ln_debt `always'"
local q3  "s_it = alpha_i + lambda_t + beta_B b_it + epsilon_it"
local m4  "B_all_core"
local r4  "vulnerability100 readiness100 ln_debt `always'"
local q4  "s_it = alpha_i + lambda_t + beta_X X_it + beta_A A_it + beta_B b_it + epsilon_it"
local m5  "C_macro"
local r5  "vulnerability100 readiness100 ln_debt `always' inflation_cpi"
local q5  "s_it = alpha_i + lambda_t + beta_X X_it + beta_A A_it + beta_B b_it + Gamma_macro W_it + epsilon_it"
local m6  "Layer1_X"
local r6  "vulnerability100 ln_debt `always' inflation_cpi reserves tt"
local q6  "s_it = alpha_i + lambda_t + beta_X X_it + beta_B b_it + Gamma_Xs W_it + epsilon_it"
local m7  "Layer2_A"
local r7  "vulnerability100 readiness100 ln_debt `always' inflation_cpi reserves tt"
local q7  "s_it = alpha_i + lambda_t + beta_A A_it + beta_X X_it + beta_B b_it + Gamma_As W_it + epsilon_it"
local m8  "Interact_AB"
local r8  "c_A c_X c_b int_AB `always' inflation_cpi reserves tt"
local q8  "s_it = alpha_i + lambda_t + beta_A A_c + beta_X X_c + beta_B b_c + beta_AB(A_c*b_c) + Gamma W_it + epsilon_it"
local m9  "Interact_AX"
local r9  "c_A c_X c_b int_AX `always' inflation_cpi reserves tt"
local q9  "s_it = alpha_i + lambda_t + beta_A A_c + beta_X X_c + beta_B b_c + beta_AX(A_c*X_c) + Gamma W_it + epsilon_it"
local m10 "Interact_all"
local r10 "c_A c_X c_b int_AB int_AX `always' inflation_cpi reserves tt"
local q10 "s_it = alpha_i + lambda_t + beta_A A_c + beta_X X_c + beta_B b_c + beta_AB(A_c*b_c) + beta_AX(A_c*X_c) + Gamma W_it + epsilon_it"

tempname p_models p_coefs p_eq
postfile `p_models' str24 model double N countries years r2_within r2_overall df_r byte country_fe year_fe using "`outdir'/model_stats.dta", replace
postfile `p_coefs' str24 model str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/model_coefficients.dta", replace
postfile `p_eq' str24 model str244 equation using "`outdir'/equations.dta", replace

forvalues z=1/10 {
    local mid "`m`z''"
    local rhs "`r`z''"
    local equ "`q`z''"
    display as text "REGRESSION `mid': `equ'"
    quietly xtreg `y' `rhs' i.year if sample_common, fe
    local __r2w = e(r2_w)
    local __r2o = e(r2_o)
    quietly areg `y' `rhs' i.year if sample_common, absorb(country_id) vce(robust)
    estimates store `mid'
    quietly levelsof country_id if e(sample), local(__countries)
    local ng : word count `__countries'
    quietly levelsof year if e(sample), local(__years)
    local nt : word count `__years'
    post `p_models' ("`mid'") (e(N)) (`ng') (`nt') (`__r2w') (`__r2o') (e(df_r)) (1) (1)
    post `p_eq' ("`mid'") ("`equ'")
    foreach v of local rhs {
        capture scalar __b = _b[`v']
        if _rc {
            post `p_coefs' ("`mid'") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        }
        else {
            scalar __se = _se[`v']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
            scalar __crit = invttail(e(df_r),.025)
            scalar __lo = __b-__crit*__se
            scalar __hi = __b+__crit*__se
            scalar __om = (__se==0)
            post `p_coefs' ("`mid'") ("`v'") (__b) (__se) (__t) (__p) (__lo) (__hi) (__om)
        }
    }
}
postclose `p_models'
postclose `p_coefs'
postclose `p_eq'
foreach f in model_stats model_coefficients equations {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* Coefficient change relative to the no-controls all-core model (B_all_core).
tempname p_change
postfile `p_change' str24 model str32 variable double baseline new absolute_change percent_change str20 reporting_rule using "`outdir'/coefficient_changes.dta", replace
estimates restore B_all_core
scalar base_X = _b[vulnerability100]
scalar base_A = _b[readiness100]
scalar base_b = _b[ln_debt]
foreach mid in C_macro Layer1_X Layer2_A {
    estimates restore `mid'
    foreach pair in "vulnerability100 base_X" "readiness100 base_A" "ln_debt base_b" {
        gettoken v bscalar : pair
        capture scalar newb = _b[`v']
        if !_rc {
            scalar abschange = newb-scalar(`bscalar')
            if abs(scalar(`bscalar'))<1e-8 {
                post `p_change' ("`mid'") ("`v'") (scalar(`bscalar')) (newb) (abschange) (.) ("absolute; near zero")
            }
            else {
                scalar pctchange = 100*abschange/abs(scalar(`bscalar'))
                post `p_change' ("`mid'") ("`v'") (scalar(`bscalar')) (newb) (abschange) (pctchange) ("percent")
            }
        }
    }
}
postclose `p_change'
preserve
    use "`outdir'/coefficient_changes.dta", clear
    export delimited using "`outdir'/coefficient_changes.csv", replace
restore

* Wald tests for interaction models.
tempname p_wald
postfile `p_wald' str24 model str64 hypothesis double F df_num df_den p using "`outdir'/wald_tests.dta", replace
estimates restore Interact_AB
quietly test c_A int_AB
post `p_wald' ("Interact_AB") ("c_A = int_AB = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test int_AB
post `p_wald' ("Interact_AB") ("all interactions = 0: int_AB = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
estimates restore Interact_AX
quietly test c_A int_AX
post `p_wald' ("Interact_AX") ("c_A = int_AX = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test int_AX
post `p_wald' ("Interact_AX") ("all interactions = 0: int_AX = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
estimates restore Interact_all
quietly test c_A int_AB
post `p_wald' ("Interact_all") ("c_A = int_AB = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test c_A int_AX
post `p_wald' ("Interact_all") ("c_A = int_AX = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test c_A int_AB int_AX
post `p_wald' ("Interact_all") ("c_A = int_AB = int_AX = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test int_AB int_AX
post `p_wald' ("Interact_all") ("all interactions = 0: int_AB = int_AX = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
postclose `p_wald'
preserve
    use "`outdir'/wald_tests.dta", clear
    export delimited using "`outdir'/wald_tests.csv", replace
restore

* Delta-method marginal effects at required moderator values.
tempname p_me p_thr
postfile `p_me' str24 model str20 moderator str20 point double moderator_value marginal_effect se t p ci_low ci_high using "`outdir'/marginal_effects.dta", replace
postfile `p_thr' str24 model str20 moderator double threshold sample_min sample_max byte in_range using "`outdir'/thresholds.dta", replace

* Utility blocks are expanded explicitly to keep the do-file dependency-free.
foreach spec in "Interact_AB ln_debt int_AB" "Interact_AX vulnerability100 int_AX" {
    gettoken mid rest : spec
    gettoken moderator interaction : rest
    estimates restore `mid'
    local mmean = scalar(mean_`moderator')
    local msd   = scalar(sd_`moderator')
    local pnames "P10 P25 P50 P75 P90 Mean_minus_1SD Mean Mean_plus_1SD"
    local pvals  "`=scalar(p10_`moderator')' `=scalar(p25_`moderator')' `=scalar(p50_`moderator')' `=scalar(p75_`moderator')' `=scalar(p90_`moderator')' `=`mmean'-`msd'' `mmean' `=`mmean'+`msd''"
    forvalues h=1/8 {
        local pn : word `h' of `pnames'
        local pv : word `h' of `pvals'
        local centered = `pv'-`mmean'
        quietly lincom c_A + (`centered')*`interaction'
        post `p_me' ("`mid'") ("`moderator'") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    scalar threshold = `mmean' - _b[c_A]/_b[`interaction']
    scalar inrange = (threshold>=scalar(min_`moderator') & threshold<=scalar(max_`moderator'))
    post `p_thr' ("`mid'") ("`moderator'") (threshold) (scalar(min_`moderator')) (scalar(max_`moderator')) (inrange)
}

* Joint-interaction model: vary one moderator while holding the other at its mean.
estimates restore Interact_all
foreach spec in "ln_debt int_AB" "vulnerability100 int_AX" {
    gettoken moderator interaction : spec
    local mmean = scalar(mean_`moderator')
    local msd   = scalar(sd_`moderator')
    local pnames "P10 P25 P50 P75 P90 Mean_minus_1SD Mean Mean_plus_1SD"
    local pvals  "`=scalar(p10_`moderator')' `=scalar(p25_`moderator')' `=scalar(p50_`moderator')' `=scalar(p75_`moderator')' `=scalar(p90_`moderator')' `=`mmean'-`msd'' `mmean' `=`mmean'+`msd''"
    forvalues h=1/8 {
        local pn : word `h' of `pnames'
        local pv : word `h' of `pvals'
        local centered = `pv'-`mmean'
        quietly lincom c_A + (`centered')*`interaction'
        post `p_me' ("Interact_all") ("`moderator'") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    scalar threshold = `mmean' - _b[c_A]/_b[`interaction']
    scalar inrange = (threshold>=scalar(min_`moderator') & threshold<=scalar(max_`moderator'))
    post `p_thr' ("Interact_all") ("`moderator'") (threshold) (scalar(min_`moderator')) (scalar(max_`moderator')) (inrange)
}
postclose `p_me'
postclose `p_thr'
foreach f in marginal_effects thresholds {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* Independent estimator spot-check: areg absorbed FE versus explicit LSDV.
* Coefficients and heteroskedasticity-robust SEs should agree numerically.
tempname p_validate
postfile `p_validate' str24 model str32 variable double main_b lsdv_b abs_b_diff main_se lsdv_se abs_se_diff using "`outdir'/validation_checks.dta", replace
foreach mid in Layer2_A Interact_all {
    if "`mid'"=="Layer2_A" local vrhs "vulnerability100 readiness100 ln_debt `always' inflation_cpi reserves tt"
    if "`mid'"=="Interact_all" local vrhs "c_A c_X c_b int_AB int_AX `always' inflation_cpi reserves tt"
    estimates restore `mid'
    foreach v of local vrhs {
        scalar mainb_`v' = _b[`v']
        scalar mainse_`v' = _se[`v']
    }
    quietly regress `y' `vrhs' i.country_id i.year if sample_common, vce(robust)
    foreach v of local vrhs {
        scalar lsb = _b[`v']
        scalar lsse = _se[`v']
        post `p_validate' ("`mid'") ("`v'") (scalar(mainb_`v')) (lsb) (abs(scalar(mainb_`v')-lsb)) (scalar(mainse_`v')) (lsse) (abs(scalar(mainse_`v')-lsse))
    }
}
postclose `p_validate'
preserve
    use "`outdir'/validation_checks.dta", clear
    export delimited using "`outdir'/validation_checks.csv", replace
restore

* Run-level metadata and an observation-level sample audit (no observations dropped).
preserve
    keep country_name iso3 country_id year ConstantGDP ln_debt growth ln_constantgdp sample_common duplicate_key
    export delimited using "`outdir'/sample_audit.csv", replace
restore

tempname p_meta
postfile `p_meta' str40 item double value using "`outdir'/run_metadata.dta", replace
post `p_meta' ("raw_observations") (scalar(N_raw))
post `p_meta' ("duplicate_country_year_rows") (scalar(N_duplicate_rows))
post `p_meta' ("nonpositive_ConstantGDP") (scalar(N_nonpositive_constant_gdp))
post `p_meta' ("nonpositive_debt") (scalar(N_nonpositive_debt))
post `p_meta' ("common_sample_observations") (scalar(N_common))
post `p_meta' ("common_sample_loss") (scalar(N_common_lost))
post `p_meta' ("common_sample_countries") (scalar(G_common))
post `p_meta' ("common_sample_years") (scalar(T_common))
post `p_meta' ("common_sample_first_year") (scalar(year_min_common))
post `p_meta' ("common_sample_last_year") (scalar(year_max_common))
post `p_meta' ("twfe_condition_number") (scalar(condition_number))
postclose `p_meta'
preserve
    use "`outdir'/run_metadata.dta", clear
    export delimited using "`outdir'/run_metadata.csv", replace
restore

display as result "ANALYSIS COMPLETE. Common sample N=" scalar(N_common) ", countries=" scalar(G_common) ", years=" scalar(T_common)
display as result "All results written to `outdir'."
log close mainlog
exit, clear
