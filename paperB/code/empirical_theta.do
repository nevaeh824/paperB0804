version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Empirical adaptation-capacity theta workflow.
*
* 1. Reproduce the baseline complete quadratic sovereign-spread model.
* 2. Estimate the one-period-ahead tax-base equation.
* 3. Construct marginal spread relief, marginal tax-base benefit, and theta.
*
* The source CSV is read only. No row is deleted, no variable is winsorized, and
* all estimation exclusions are represented by explicit sample flags.
* Inference follows baseline/WORKFLOW.md: country and year fixed effects with
* observation-level Huber-White robust standard errors (not country clustering).
* -----------------------------------------------------------------------------

args project
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0804"
local datadir     "`project'/data0804"
local baselinedir "`project'/baseline/stata_outputs"
local workflowdir "`project'/empirical_theta"
local outdir      "`workflowdir'/stata_outputs"

capture mkdir "`workflowdir'"
capture mkdir "`outdir'"
capture log close _all
log using "`outdir'/empirical_theta.log", text replace name(mainlog)

display as text "ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "SOURCE: `datadir'/invest_panel_weo.csv"
display as text "BASELINE SOURCE: `baselinedir'/model_coefficients.csv"
display as text "POLICY: source preserved; exact panel time operators; explicit sample flags; no silent deletion."

import delimited using "`datadir'/invest_panel_weo.csv", clear varnames(1) case(preserve) encoding(UTF-8)
compress
count
scalar N_raw = r(N)

* Unified regression-unit convention inherited from baseline: all source rates,
* percentages, and 0--100 indices enter as 0--1 ratios. GDP and other monetary
* amounts stay in their source units. Variable names are retained for downstream
* compatibility, and an explicit audit records every conversion.
local ratio_vars bond_spreads bond_10y vulnerability100 readiness100 growth inflation_cpi debt_gdp PrimaryBalance_gdp reserves tt Revenue_gdp OverallBalance_gdp interest_revenue
tempname p_units
postfile `p_units' str32 variable double source_min source_max ratio_min ratio_max max_abs_scaling_diff byte passed using "`outdir'/unit_scaling_checks.dta", replace
foreach v of local ratio_vars {
    confirm variable `v'
    recast double `v'
    quietly summarize `v', meanonly
    scalar __source_min = r(min)
    scalar __source_max = r(max)
    generate double __source_value = `v'
    replace `v' = `v'/100
    generate double __scale_diff = abs(`v'-__source_value/100) if !missing(__source_value)
    quietly summarize __scale_diff, meanonly
    scalar __max_diff = cond(r(N)>0,r(max),0)
    quietly summarize `v', meanonly
    post `p_units' ("`v'") (scalar(__source_min)) (scalar(__source_max)) (r(min)) (r(max)) (scalar(__max_diff)) (scalar(__max_diff)<=1e-12)
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
label variable vulnerability100 "ND-GAIN vulnerability ratio; source index divided by 100"
label variable readiness100 "ND-GAIN readiness ratio; source index divided by 100"
label variable debt_gdp "Government debt/GDP ratio; source percentage divided by 100"
label variable growth "Real GDP growth ratio; source percentage divided by 100"
label variable inflation_cpi "CPI inflation ratio; source percentage divided by 100"
label variable interest_revenue "Interest/revenue ratio; source percentage divided by 100"

* Construct the theoretical debt state directly from same-period source amounts.
* The explicit b_it_theta name is retained in generated panels so downstream
* workflows can audit the exact debt/CurrentGDP mapping.
confirm variable debt
confirm variable CurrentGDP
recast double debt CurrentGDP
generate double b_it_theta = debt/CurrentGDP if CurrentGDP>0 & !missing(debt)
label variable b_it_theta "b_it used in theta construction: debt/CurrentGDP"
generate double ln_currentgdp = ln(CurrentGDP) if CurrentGDP>0
label variable ln_currentgdp "Log of same-period current-price GDP"

egen long country_id = group(iso3), label
label variable country_id "Numeric country identifier generated from iso3"

duplicates tag iso3 year, generate(duplicate_key)
quietly count if duplicate_key>0
scalar N_duplicate_rows = r(N)
preserve
    keep if duplicate_key>0
    keep country_name iso3 year duplicate_key
    sort iso3 year
    export delimited using "`outdir'/duplicate_country_year.csv", replace
restore
if scalar(N_duplicate_rows)>0 {
    display as error "Duplicate country-year keys exist. No rows were deleted. Workflow stopped."
    log close mainlog
    exit 459
}

xtset country_id year

* Baseline transformation and exact time-aligned tax-base variables.
quietly count if CurrentGDP<=0 & !missing(CurrentGDP)
scalar N_nonpositive_current_gdp = r(N)

generate double revenue_lead = F.revenue
generate double currentgdp_lag = L.CurrentGDP
generate double taxbase_lead = revenue_lead/CurrentGDP if CurrentGDP>0 & !missing(revenue_lead)
generate double taxbase_lag = revenue/currentgdp_lag if currentgdp_lag>0 & !missing(revenue)
generate int outcome_year = year + 1 if !missing(revenue_lead)

label variable revenue_lead "Revenue at t+1 (exact one-year panel lead)"
label variable currentgdp_lag "CurrentGDP at t-1 (exact one-year panel lag)"
label variable taxbase_lead "Revenue(t+1)/CurrentGDP(t); ratio"
label variable taxbase_lag "Revenue(t)/CurrentGDP(t-1); ratio"
label variable outcome_year "Calendar year of revenue numerator in taxbase_lead"

* Recreate the baseline common sample exactly.
local spread_controls growth inflation_cpi reserves tt ln_currentgdp
local spread_modelvars bond_spreads vulnerability100 readiness100 b_it_theta `spread_controls'
egen int spread_missing_count = rowmiss(`spread_modelvars')
generate byte sample_spread = (spread_missing_count==0)
label variable sample_spread "Exact baseline common sample"

* The tax equation is the explicit exception: it excludes ln(CurrentGDP).
local tax_controls growth inflation_cpi reserves tt
local tax_modelvars taxbase_lead readiness100 vulnerability100 taxbase_lag b_it_theta `tax_controls'
egen int tax_missing_count = rowmiss(`tax_modelvars')
generate byte sample_tax = (tax_missing_count==0)
label variable sample_tax "Common nonmissing sample for tax-base model"

generate byte sample_theta_support = sample_spread & sample_tax
label variable sample_theta_support "Overlap of spread and tax estimation samples"

* Sample counts and coverage.
foreach s in spread tax theta_support {
    quietly count if sample_`s'
    scalar N_`s' = r(N)
    egen byte tag_country_`s' = tag(country_id) if sample_`s'
    egen byte tag_year_`s' = tag(year) if sample_`s'
    quietly count if tag_country_`s'==1
    scalar G_`s' = r(N)
    quietly count if tag_year_`s'==1
    scalar T_`s' = r(N)
    quietly summarize year if sample_`s', meanonly
    scalar year_min_`s' = r(min)
    scalar year_max_`s' = r(max)
}

* Missing-data audit for every tax-model input.
tempname p_missing
postfile `p_missing' str32 variable double missing_total missing_rate exclusive_loss using "`outdir'/missing_loss.dta", replace
foreach v of local tax_modelvars {
    local others : list tax_modelvars - v
    quietly count if missing(`v')
    local mt = r(N)
    capture drop __other_missing
    egen int __other_missing = rowmiss(`others')
    quietly count if missing(`v') & __other_missing==0
    local ex = r(N)
    post `p_missing' ("`v'") (`mt') (100*`mt'/scalar(N_raw)) (`ex')
}
capture drop __other_missing
postclose `p_missing'
preserve
    use "`outdir'/missing_loss.dta", clear
    export delimited using "`outdir'/missing_loss.csv", replace
restore

* Tax-model profile, panel variation, absorption, correlations, and collinearity.
local tax_profilevars taxbase_lead taxbase_lag readiness100 vulnerability100 b_it_theta growth inflation_cpi reserves tt

tempname p_profile
postfile `p_profile' str32 variable double N missing missing_rate mean sd min p10 p25 p50 p75 p90 max using "`outdir'/profile.dta", replace
foreach v of local tax_profilevars {
    quietly count if !missing(`v')
    local n = r(N)
    quietly count if missing(`v')
    local m = r(N)
    quietly summarize `v', detail
    post `p_profile' ("`v'") (`n') (`m') (100*`m'/scalar(N_raw)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
postclose `p_profile'
preserve
    use "`outdir'/profile.dta", clear
    export delimited using "`outdir'/profile.csv", replace
restore

tempname p_variation
postfile `p_variation' str32 variable double sd_overall sd_between sd_within ratio_within_overall str24 fe_identification using "`outdir'/variation.dta", replace
foreach v of local tax_profilevars {
    quietly xtsum `v' if sample_tax
    local sdo = r(sd)
    local sdb = r(sd_b)
    local sdw = r(sd_w)
    local ratio = cond(`sdo'>0,`sdw'/`sdo',.)
    local ident "adequate"
    if missing(`sdw') | `sdw'<=1e-10*max(1,`sdo') local ident "not_identified_by_FE"
    else if `ratio'<.01 local ident "low_within_variation"
    post `p_variation' ("`v'") (`sdo') (`sdb') (`sdw') (`ratio') ("`ident'")
}
postclose `p_variation'
preserve
    use "`outdir'/variation.dta", clear
    export delimited using "`outdir'/variation.csv", replace
restore

tempname p_absorption
postfile `p_absorption' str32 variable byte country_absorbed time_absorbed twfe_absorbed double residual_sd tolerance using "`outdir'/absorption.dta", replace
foreach v of local tax_profilevars {
    capture drop __sd_i __sd_t __twres
    bysort country_id: egen double __sd_i = sd(`v') if sample_tax
    quietly summarize __sd_i, meanonly
    local maxsdi = cond(missing(r(max)),0,r(max))
    bysort year: egen double __sd_t = sd(`v') if sample_tax
    quietly summarize __sd_t, meanonly
    local maxsdt = cond(missing(r(max)),0,r(max))
    quietly summarize `v' if sample_tax
    local tol = 1e-10*max(1,r(sd))
    quietly regress `v' i.country_id i.year if sample_tax
    predict double __twres if e(sample), residuals
    quietly summarize __twres
    local rsd = cond(missing(r(sd)),0,r(sd))
    post `p_absorption' ("`v'") (`maxsdi'<=`tol') (`maxsdt'<=`tol') (`rsd'<=`tol') (`rsd') (`tol')
}
postclose `p_absorption'
capture drop __sd_i __sd_t __twres
preserve
    use "`outdir'/absorption.dta", clear
    export delimited using "`outdir'/absorption.csv", replace
restore

local tax_corrvars readiness100 vulnerability100 taxbase_lag growth inflation_cpi reserves tt
quietly correlate `tax_corrvars' if sample_tax
matrix TAXCORR = r(C)
tempname p_corr
postfile `p_corr' str32 variable_i str32 variable_j double correlation using "`outdir'/correlations.dta", replace
local i = 0
foreach vi of local tax_corrvars {
    local ++i
    local j = 0
    foreach vj of local tax_corrvars {
        local ++j
        post `p_corr' ("`vi'") ("`vj'") (TAXCORR[`i',`j'])
    }
}
postclose `p_corr'
preserve
    use "`outdir'/correlations.dta", clear
    export delimited using "`outdir'/correlations.csv", replace
restore

* Center interacting variables within their own fixed estimation samples.
tempname p_center
postfile `p_center' str16 sample str32 variable double mean sd min p10 p25 p50 p75 p90 max using "`outdir'/centering.dta", replace

foreach v in readiness100 b_it_theta vulnerability100 {
    quietly summarize `v' if sample_spread, detail
    scalar spread_mean_`v' = r(mean)
    scalar spread_sd_`v' = r(sd)
    post `p_center' ("spread") ("`v'") (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
foreach v in readiness100 vulnerability100 {
    quietly summarize `v' if sample_tax, detail
    scalar tax_mean_`v' = r(mean)
    scalar tax_sd_`v' = r(sd)
    scalar tax_min_`v' = r(min)
    scalar tax_p10_`v' = r(p10)
    scalar tax_p25_`v' = r(p25)
    scalar tax_p50_`v' = r(p50)
    scalar tax_p75_`v' = r(p75)
    scalar tax_p90_`v' = r(p90)
    scalar tax_max_`v' = r(max)
    post `p_center' ("tax") ("`v'") (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
postclose `p_center'

generate double c_A = readiness100 - scalar(spread_mean_readiness100)
generate double c_b = b_it_theta - scalar(spread_mean_b_it_theta)
generate double c_X = vulnerability100 - scalar(spread_mean_vulnerability100)
generate double half_A2 = 0.5*c_A^2
generate double half_b2 = 0.5*c_b^2
generate double half_X2 = 0.5*c_X^2
generate double int_AB = c_A*c_b
generate double int_AX = c_A*c_X
generate double int_bX = c_b*c_X

generate double c_A_T = readiness100 - scalar(tax_mean_readiness100)
generate double c_X_T = vulnerability100 - scalar(tax_mean_vulnerability100)
generate double half_A2_T = 0.5*c_A_T^2
generate double half_X2_T = 0.5*c_X_T^2
generate double int_AX_T = c_A_T*c_X_T

label variable c_A "readiness100 centered on spread sample"
label variable c_b "b_it=debt/CurrentGDP centered on spread sample"
label variable c_X "vulnerability100 centered on spread sample"
label variable half_A2 "0.5 times c_A squared"
label variable half_b2 "0.5 times c_b squared"
label variable half_X2 "0.5 times c_X squared"
label variable int_AB "c_A times c_b"
label variable int_AX "c_A times c_X"
label variable int_bX "c_b times c_X"
label variable c_A_T "readiness100 centered on tax sample"
label variable c_X_T "vulnerability100 centered on tax sample"
label variable half_A2_T "0.5 times tax-sample centered readiness squared"
label variable half_X2_T "0.5 times tax-sample centered vulnerability squared"
label variable int_AX_T "c_A_T times c_X_T"

preserve
    use "`outdir'/centering.dta", clear
    export delimited using "`outdir'/centering.csv", replace
restore

* VIF after removing country and year fixed effects, for the full linear and
* full interaction specifications separately.
local vif_linear readiness100 vulnerability100 taxbase_lag growth inflation_cpi reserves tt
local vif_interaction c_A_T c_X_T int_AX_T taxbase_lag growth inflation_cpi reserves tt
local vif_quadratic c_A_T c_X_T half_A2_T half_X2_T int_AX_T taxbase_lag b_it_theta growth inflation_cpi reserves tt
local vif_all : list vif_linear | vif_interaction
local vif_all : list vif_all | vif_quadratic
foreach v of local vif_all {
    quietly regress `v' i.country_id i.year if sample_tax
    predict double tw_`v' if sample_tax, residuals
}
tempname p_vif
postfile `p_vif' str24 specification str32 variable double vif tolerance condition_number using "`outdir'/collinearity.dta", replace
foreach spec in linear interaction quadratic {
    local vars `vif_`spec''
    local residuals
    foreach v of local vars {
        local residuals `residuals' tw_`v'
    }
    quietly correlate `residuals' if sample_tax
    matrix __R = r(C)
    mata: st_numscalar("condition_`spec'", sqrt(cond(st_matrix("__R"))))
    foreach v of local vars {
        local rv tw_`v'
        local others : list residuals - rv
        quietly regress `rv' `others' if sample_tax
        local vif = 1/(1-e(r2))
        post `p_vif' ("`spec'") ("`v'") (`vif') (1/`vif') (scalar(condition_`spec'))
    }
}
postclose `p_vif'
preserve
    use "`outdir'/collinearity.dta", clear
    export delimited using "`outdir'/collinearity.csv", replace
restore

* Model-output collectors.
tempname p_models p_coefs p_equations p_construct
postfile `p_models' str28 model double N countries years first_year last_year r2_within r2_overall df_r byte country_fe year_fe macro_controls external_controls interaction using "`outdir'/model_stats.dta", replace
postfile `p_coefs' str28 model str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/model_coefficients.dta", replace
postfile `p_equations' str28 model str244 equation using "`outdir'/equations.dta", replace
postfile `p_construct' str20 source str32 parameter double estimate se t p ci_low ci_high str48 units using "`outdir'/construction_coefficients.dta", replace

* -----------------------------------------------------------------------------
* Baseline complete quadratic model, reproduced on the locked baseline sample.
* -----------------------------------------------------------------------------
local spread_rhs c_A c_b c_X half_A2 half_b2 half_X2 int_AB int_AX int_bX growth inflation_cpi reserves tt ln_currentgdp
quietly xtreg bond_spreads `spread_rhs' i.year if sample_spread, fe
local spread_r2w = e(r2_w)
local spread_r2o = e(r2_o)
quietly areg bond_spreads `spread_rhs' i.year if sample_spread, absorb(country_id) vce(robust)
estimates store Spread_Quadratic_all
post `p_models' ("Spread_Quadratic_all") (e(N)) (scalar(G_spread)) (scalar(T_spread)) (scalar(year_min_spread)) (scalar(year_max_spread)) (`spread_r2w') (`spread_r2o') (e(df_r)) (1) (1) (1) (1) (1)
post `p_equations' ("Spread_Quadratic_all") ("s_it = FE_i + FE_t + centered quadratic A,b,X + controls + eta_G*ln(CurrentGDP) + error")

foreach v of local spread_rhs {
    capture scalar __b = _b[`v']
    if _rc {
        post `p_coefs' ("Spread_Quadratic_all") ("`v'") (.) (.) (.) (.) (.) (.) (1)
    }
    else {
        scalar __se = _se[`v']
        scalar __t = cond(__se>0,__b/__se,.)
        scalar __p = cond(__se>0,2*ttail(e(df_r),abs(__t)),.)
        scalar __crit = invttail(e(df_r),.025)
        post `p_coefs' ("Spread_Quadratic_all") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
    }
}

scalar beta_A_centered = _b[c_A]
scalar beta_b_centered = _b[c_b]
scalar beta_X_centered = _b[c_X]
scalar beta_AA = _b[half_A2]
scalar beta_bb = _b[half_b2]
scalar beta_XX = _b[half_X2]
scalar beta_AB = _b[int_AB]
scalar beta_AX = _b[int_AX]
scalar beta_bX = _b[int_bX]
scalar beta_A_raw = scalar(beta_A_centered) - scalar(beta_AA)*scalar(spread_mean_readiness100) - scalar(beta_AB)*scalar(spread_mean_b_it_theta) - scalar(beta_AX)*scalar(spread_mean_vulnerability100)
scalar beta_b_raw = scalar(beta_b_centered) - scalar(beta_bb)*scalar(spread_mean_b_it_theta) - scalar(beta_AB)*scalar(spread_mean_readiness100) - scalar(beta_bX)*scalar(spread_mean_vulnerability100)
scalar beta_X_raw = scalar(beta_X_centered) - scalar(beta_XX)*scalar(spread_mean_vulnerability100) - scalar(beta_AX)*scalar(spread_mean_readiness100) - scalar(beta_bX)*scalar(spread_mean_b_it_theta)

quietly lincom c_A - scalar(spread_mean_readiness100)*half_A2 - scalar(spread_mean_b_it_theta)*int_AB - scalar(spread_mean_vulnerability100)*int_AX
post `p_construct' ("spread") ("beta_A_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per A-ratio unit")
quietly lincom c_b - scalar(spread_mean_b_it_theta)*half_b2 - scalar(spread_mean_readiness100)*int_AB - scalar(spread_mean_vulnerability100)*int_bX
post `p_construct' ("spread") ("beta_b_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per debt-ratio unit")
quietly lincom c_X - scalar(spread_mean_vulnerability100)*half_X2 - scalar(spread_mean_readiness100)*int_AX - scalar(spread_mean_b_it_theta)*int_bX
post `p_construct' ("spread") ("beta_X_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per X-ratio unit")
foreach pair in "beta_AA half_A2" "beta_bb half_b2" "beta_XX half_X2" "beta_AB int_AB" "beta_AX int_AX" "beta_bX int_bX" {
    gettoken parameter variable : pair
    quietly lincom `variable'
    post `p_construct' ("spread") ("`parameter'") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("second-order spread coefficient")
}

* -----------------------------------------------------------------------------
* Eleven tax-base models on one locked common sample. Models 1--10 retain the
* prior progression. Model 11 is the requested complete centered quadratic tax
* equation and is the sole source of the reported marginal tax-base benefit.
* -----------------------------------------------------------------------------
local tm1  "T1_X_only"
local tr1  "vulnerability100"
local tq1  "Tlead = FE_i + FE_t + gamma_X X_it + error"
local mc1  0
local ec1  0
local ix1  0

local tm2  "T2_A_only"
local tr2  "readiness100"
local tq2  "Tlead = FE_i + FE_t + gamma_A A_it + error"
local mc2  0
local ec2  0
local ix2  0

local tm3  "T3_persistence"
local tr3  "taxbase_lag"
local tq3  "Tlead = FE_i + FE_t + rho_T Tlag + error"
local mc3  0
local ec3  0
local ix3  0

local tm4  "T4_all_core"
local tr4  "vulnerability100 readiness100 taxbase_lag"
local tq4  "Tlead = FE_i + FE_t + gamma_X X_it + gamma_A A_it + rho_T Tlag + error"
local mc4  0
local ec4  0
local ix4  0

local tm5  "T5_macro"
local tr5  "vulnerability100 readiness100 taxbase_lag growth inflation_cpi"
local tq5  "Tlead = FE_i + FE_t + core + Gamma_macro W_macro + error"
local mc5  1
local ec5  0
local ix5  0

local tm6  "T6_layer1_X"
local tr6  "vulnerability100 taxbase_lag growth inflation_cpi reserves tt"
local tq6  "Tlead = FE_i + FE_t + gamma_X X_it + rho_T Tlag + Gamma W + error"
local mc6  1
local ec6  1
local ix6  0

local tm7  "T7_layer2_A"
local tr7  "vulnerability100 readiness100 taxbase_lag growth inflation_cpi reserves tt"
local tq7  "Tlead = FE_i + FE_t + gamma_A A_it + gamma_X X_it + rho_T Tlag + Gamma W + error"
local mc7  1
local ec7  1
local ix7  0

local tm8  "T8_interact_core"
local tr8  "c_A_T c_X_T int_AX_T taxbase_lag"
local tq8  "Tlead = FE_i + FE_t + gamma_A A_c + gamma_X X_c + gamma_AX(A_c*X_c) + rho_T Tlag + error"
local mc8  0
local ec8  0
local ix8  1

local tm9  "T9_interact_macro"
local tr9  "c_A_T c_X_T int_AX_T taxbase_lag growth inflation_cpi"
local tq9  "Tlead = FE_i + FE_t + centered interaction core + Gamma_macro W_macro + error"
local mc9  1
local ec9  0
local ix9  1

local tm10 "T10_interact_full"
local tr10 "c_A_T c_X_T int_AX_T taxbase_lag growth inflation_cpi reserves tt"
local tq10 "Tlead = FE_i + FE_t + centered interaction core + Gamma W + error"
local mc10 1
local ec10 1
local ix10 1

local tm11 "T11_quadratic_full"
local tr11 "c_A_T c_X_T half_A2_T half_X2_T int_AX_T taxbase_lag b_it_theta growth inflation_cpi reserves tt"
local tq11 "Tlead = FE_i + FE_t + centered quadratic A,X + rho_T*Tlag + phi_b*b + controls + error"
local mc11 1
local ec11 1
local ix11 1

forvalues z=1/11 {
    local mid "`tm`z''"
    local rhs "`tr`z''"
    local equ "`tq`z''"
    display as text "TAX REGRESSION `mid': `equ'"
    quietly xtreg taxbase_lead `rhs' i.year if sample_tax, fe
    local __r2w = e(r2_w)
    local __r2o = e(r2_o)
    quietly areg taxbase_lead `rhs' i.year if sample_tax, absorb(country_id) vce(robust)
    estimates store `mid'
    post `p_models' ("`mid'") (e(N)) (scalar(G_tax)) (scalar(T_tax)) (scalar(year_min_tax)) (scalar(year_max_tax)) (`__r2w') (`__r2o') (e(df_r)) (1) (1) (`mc`z'') (`ec`z'') (`ix`z'')
    post `p_equations' ("`mid'") ("`equ'")
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
            post `p_coefs' ("`mid'") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}

* Preferred marginal tax-base coefficients are from the requested complete
* quadratic specification with persistence, b_it, and all non-scale controls.
estimates restore T11_quadratic_full
scalar gamma_A_centered = _b[c_A_T]
scalar gamma_AA = _b[half_A2_T]
scalar gamma_XX = _b[half_X2_T]
scalar gamma_AX = _b[int_AX_T]
scalar phi_b = _b[b_it_theta]
scalar gamma_A_raw = scalar(gamma_A_centered) - scalar(gamma_AA)*scalar(tax_mean_readiness100) - scalar(gamma_AX)*scalar(tax_mean_vulnerability100)

quietly lincom c_A_T - scalar(tax_mean_readiness100)*half_A2_T - scalar(tax_mean_vulnerability100)*int_AX_T
post `p_construct' ("tax") ("gamma_A_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("revenue/GDP ratio per A-ratio unit")
quietly lincom half_A2_T
post `p_construct' ("tax") ("gamma_AA") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("tax-base quadratic coefficient in A")
quietly lincom half_X2_T
post `p_construct' ("tax") ("gamma_XX") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("tax-base quadratic coefficient in X")
quietly lincom int_AX_T
post `p_construct' ("tax") ("gamma_AX") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("revenue/GDP ratio per A-ratio per X-ratio unit")
quietly lincom b_it_theta
post `p_construct' ("tax") ("phi_b") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("tax-base ratio per b-ratio unit")

postclose `p_models'
postclose `p_coefs'
postclose `p_equations'
postclose `p_construct'
foreach f in model_stats model_coefficients equations construction_coefficients {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* Coefficient changes as controls are added to linear and interaction models.
tempname p_changes
postfile `p_changes' str28 baseline_model str28 model str32 variable double baseline new absolute_change percent_change str24 reporting_rule using "`outdir'/coefficient_changes.dta", replace
estimates restore T4_all_core
foreach v in vulnerability100 readiness100 taxbase_lag {
    scalar base_linear_`v' = _b[`v']
}
foreach mid in T5_macro T7_layer2_A {
    estimates restore `mid'
    foreach v in vulnerability100 readiness100 taxbase_lag {
        scalar __new = _b[`v']
        scalar __change = __new-scalar(base_linear_`v')
        if abs(scalar(base_linear_`v'))<1e-8 post `p_changes' ("T4_all_core") ("`mid'") ("`v'") (scalar(base_linear_`v')) (__new) (__change) (.) ("absolute; near zero")
        else post `p_changes' ("T4_all_core") ("`mid'") ("`v'") (scalar(base_linear_`v')) (__new) (__change) (100*__change/abs(scalar(base_linear_`v'))) ("percent")
    }
}
estimates restore T8_interact_core
foreach v in c_A_T c_X_T int_AX_T taxbase_lag {
    scalar base_interaction_`v' = _b[`v']
}
foreach mid in T9_interact_macro T10_interact_full {
    estimates restore `mid'
    foreach v in c_A_T c_X_T int_AX_T taxbase_lag {
        scalar __new = _b[`v']
        scalar __change = __new-scalar(base_interaction_`v')
        if abs(scalar(base_interaction_`v'))<1e-8 post `p_changes' ("T8_interact_core") ("`mid'") ("`v'") (scalar(base_interaction_`v')) (__new) (__change) (.) ("absolute; near zero")
        else post `p_changes' ("T8_interact_core") ("`mid'") ("`v'") (scalar(base_interaction_`v')) (__new) (__change) (100*__change/abs(scalar(base_interaction_`v'))) ("percent")
    }
}
postclose `p_changes'
preserve
    use "`outdir'/coefficient_changes.dta", clear
    export delimited using "`outdir'/coefficient_changes.csv", replace
restore

* Joint tests for control blocks and interaction terms.
tempname p_wald
postfile `p_wald' str28 model str80 hypothesis double F df_num df_den p using "`outdir'/wald_tests.dta", replace
estimates restore T5_macro
quietly test growth inflation_cpi
post `p_wald' ("T5_macro") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
estimates restore T7_layer2_A
quietly test reserves tt
post `p_wald' ("T7_layer2_A") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test growth inflation_cpi reserves tt
post `p_wald' ("T7_layer2_A") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
foreach mid in T8_interact_core T9_interact_macro T10_interact_full {
    estimates restore `mid'
    quietly test c_A_T int_AX_T
    post `p_wald' ("`mid'") ("adaptation terms jointly zero: c_A_T = int_AX_T = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
    quietly test int_AX_T
    post `p_wald' ("`mid'") ("interaction zero: int_AX_T = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
}
estimates restore T9_interact_macro
quietly test growth inflation_cpi
post `p_wald' ("T9_interact_macro") ("macro controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
estimates restore T10_interact_full
quietly test reserves tt
post `p_wald' ("T10_interact_full") ("external controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test growth inflation_cpi reserves tt
post `p_wald' ("T10_interact_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
estimates restore T11_quadratic_full
quietly test c_A_T half_A2_T int_AX_T
post `p_wald' ("T11_quadratic_full") ("marginal-A terms jointly zero: c_A_T = half_A2_T = int_AX_T = 0") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test half_A2_T half_X2_T int_AX_T
post `p_wald' ("T11_quadratic_full") ("all second-order tax terms jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test b_it_theta
post `p_wald' ("T11_quadratic_full") ("b_it coefficient zero") (r(F)) (r(df)) (r(df_r)) (r(p))
quietly test growth inflation_cpi reserves tt
post `p_wald' ("T11_quadratic_full") ("all controls jointly zero") (r(F)) (r(df)) (r(df_r)) (r(p))
postclose `p_wald'
preserve
    use "`outdir'/wald_tests.dta", clear
    export delimited using "`outdir'/wald_tests.csv", replace
restore

* Delta-method marginal tax-base benefits across the observed X distribution.
tempname p_marginal p_threshold
postfile `p_marginal' str28 model str24 moderator str20 point double moderator_value marginal_effect se t p ci_low ci_high using "`outdir'/marginal_effects.dta", replace
postfile `p_threshold' str28 model str24 moderator double threshold sample_min sample_max byte in_range using "`outdir'/thresholds.dta", replace
foreach mid in T8_interact_core T9_interact_macro T10_interact_full {
    estimates restore `mid'
    local xmean = scalar(tax_mean_vulnerability100)
    local xsd = scalar(tax_sd_vulnerability100)
    local pnames "P10 P25 P50 P75 P90 Mean_minus_1SD Mean Mean_plus_1SD"
    local pvals "`=scalar(tax_p10_vulnerability100)' `=scalar(tax_p25_vulnerability100)' `=scalar(tax_p50_vulnerability100)' `=scalar(tax_p75_vulnerability100)' `=scalar(tax_p90_vulnerability100)' `=`xmean'-`xsd'' `xmean' `=`xmean'+`xsd''"
    forvalues h=1/8 {
        local pn : word `h' of `pnames'
        local pv : word `h' of `pvals'
        local centered = `pv'-`xmean'
        quietly lincom c_A_T + (`centered')*int_AX_T
        post `p_marginal' ("`mid'") ("vulnerability100") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    scalar __threshold = `xmean' - _b[c_A_T]/_b[int_AX_T]
    scalar __inrange = (__threshold>=scalar(tax_min_vulnerability100) & __threshold<=scalar(tax_max_vulnerability100))
    post `p_threshold' ("`mid'") ("vulnerability100") (__threshold) (scalar(tax_min_vulnerability100)) (scalar(tax_max_vulnerability100)) (__inrange)
}
estimates restore T11_quadratic_full
local xmean = scalar(tax_mean_vulnerability100)
local xsd = scalar(tax_sd_vulnerability100)
local pnames "P10 P25 P50 P75 P90 Mean_minus_1SD Mean Mean_plus_1SD"
local pvals "`=scalar(tax_p10_vulnerability100)' `=scalar(tax_p25_vulnerability100)' `=scalar(tax_p50_vulnerability100)' `=scalar(tax_p75_vulnerability100)' `=scalar(tax_p90_vulnerability100)' `=`xmean'-`xsd'' `xmean' `=`xmean'+`xsd''"
forvalues h=1/8 {
    local pn : word `h' of `pnames'
    local pv : word `h' of `pvals'
    local centered = `pv'-`xmean'
    quietly lincom c_A_T + (`centered')*int_AX_T
    post `p_marginal' ("T11_quadratic_full") ("vulnerability100") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
}
scalar __threshold = `xmean' - _b[c_A_T]/_b[int_AX_T]
scalar __inrange = (__threshold>=scalar(tax_min_vulnerability100) & __threshold<=scalar(tax_max_vulnerability100))
post `p_threshold' ("T11_quadratic_full") ("vulnerability_at_mean_A") (__threshold) (scalar(tax_min_vulnerability100)) (scalar(tax_max_vulnerability100)) (__inrange)
local amean = scalar(tax_mean_readiness100)
local asd = scalar(tax_sd_readiness100)
local avals "`=scalar(tax_p10_readiness100)' `=scalar(tax_p25_readiness100)' `=scalar(tax_p50_readiness100)' `=scalar(tax_p75_readiness100)' `=scalar(tax_p90_readiness100)' `=`amean'-`asd'' `amean' `=`amean'+`asd''"
forvalues h=1/8 {
    local pn : word `h' of `pnames'
    local pv : word `h' of `avals'
    local centered = `pv'-`amean'
    quietly lincom c_A_T + (`centered')*half_A2_T
    post `p_marginal' ("T11_quadratic_full") ("readiness100") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
}
scalar __threshold = `amean' - _b[c_A_T]/_b[half_A2_T]
scalar __inrange = (__threshold>=scalar(tax_min_readiness100) & __threshold<=scalar(tax_max_readiness100))
post `p_threshold' ("T11_quadratic_full") ("readiness_at_mean_X") (__threshold) (scalar(tax_min_readiness100)) (scalar(tax_max_readiness100)) (__inrange)
postclose `p_marginal'
postclose `p_threshold'
foreach f in marginal_effects thresholds {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* -----------------------------------------------------------------------------
* Validate reproduced quadratic spread coefficients against baseline results.
* -----------------------------------------------------------------------------
estimates restore Spread_Quadratic_all
foreach v of local spread_rhs {
    scalar main_spread_`v' = _b[`v']
    scalar main_spread_se_`v' = _se[`v']
}

tempname p_baseline_validation
postfile `p_baseline_validation' str32 variable double reproduced_b baseline_b abs_b_diff reproduced_se baseline_se abs_se_diff using "`outdir'/baseline_validation.dta", replace
preserve
    import delimited using "`baselinedir'/model_coefficients.csv", clear varnames(1) case(preserve) encoding(UTF-8)
    foreach v of local spread_rhs {
        quietly summarize coefficient if model=="Quadratic_all" & variable=="`v'", meanonly
        if r(N)!=1 {
            display as error "Expected exactly one baseline coefficient for `v'; found " r(N)
            restore
            log close mainlog
            exit 459
        }
        scalar __base_b = r(mean)
        quietly summarize se if model=="Quadratic_all" & variable=="`v'", meanonly
        scalar __base_se = r(mean)
        post `p_baseline_validation' ("`v'") (scalar(main_spread_`v')) (scalar(__base_b)) (abs(scalar(main_spread_`v')-scalar(__base_b))) (scalar(main_spread_se_`v')) (scalar(__base_se)) (abs(scalar(main_spread_se_`v')-scalar(__base_se)))
    }
restore
postclose `p_baseline_validation'
preserve
    use "`outdir'/baseline_validation.dta", clear
    export delimited using "`outdir'/baseline_validation.csv", replace
restore

* Independent LSDV validation for the spread source and the principal tax models.
tempname p_estimator_validation
postfile `p_estimator_validation' str28 model str32 variable double areg_b lsdv_b abs_b_diff areg_se lsdv_se abs_se_diff using "`outdir'/estimator_validation.dta", replace
foreach model in Spread_Quadratic_all T7_layer2_A T10_interact_full T11_quadratic_full {
    estimates restore `model'
    if "`model'"=="Spread_Quadratic_all" {
        local validation_y bond_spreads
        local validation_rhs `spread_rhs'
        local validation_sample sample_spread
    }
    else if "`model'"=="T7_layer2_A" {
        local validation_y taxbase_lead
        local validation_rhs `tr7'
        local validation_sample sample_tax
    }
    else if "`model'"=="T10_interact_full" {
        local validation_y taxbase_lead
        local validation_rhs `tr10'
        local validation_sample sample_tax
    }
    else {
        local validation_y taxbase_lead
        local validation_rhs `tr11'
        local validation_sample sample_tax
    }
    foreach v of local validation_rhs {
        scalar main_b_`v' = _b[`v']
        scalar main_se_`v' = _se[`v']
    }
    quietly regress `validation_y' `validation_rhs' i.country_id i.year if `validation_sample', vce(robust)
    foreach v of local validation_rhs {
        scalar __lsb = _b[`v']
        scalar __lsse = _se[`v']
        post `p_estimator_validation' ("`model'") ("`v'") (scalar(main_b_`v')) (__lsb) (abs(scalar(main_b_`v')-__lsb)) (scalar(main_se_`v')) (__lsse) (abs(scalar(main_se_`v')-__lsse))
    }
}
postclose `p_estimator_validation'
preserve
    use "`outdir'/estimator_validation.dta", clear
    export delimited using "`outdir'/estimator_validation.csv", replace
restore

* -----------------------------------------------------------------------------
* Row-level construction from the complete centered quadratic spread model.
* -----------------------------------------------------------------------------
generate double mA_hat_spread_ratio = -(scalar(beta_A_centered) + scalar(beta_AA)*c_A + scalar(beta_AB)*c_b + scalar(beta_AX)*c_X) if !missing(c_A,c_b,c_X)
generate double mA_hat = mA_hat_spread_ratio if !missing(mA_hat_spread_ratio)
generate double spread_saving_component = b_it_theta*mA_hat if !missing(b_it_theta,mA_hat)
generate double TA_hat = scalar(gamma_A_centered) + scalar(gamma_AA)*c_A_T + scalar(gamma_AX)*c_X_T if !missing(c_A_T,c_X_T)
generate double theta_hat_A = spread_saving_component + TA_hat if !missing(spread_saving_component,TA_hat)
generate byte theta_constructible = !missing(theta_hat_A)

label variable mA_hat_spread_ratio "Marginal spread-ratio relief per readiness-ratio unit"
label variable mA_hat "Marginal spread-ratio relief from baseline quadratic model"
label variable spread_saving_component "debt/CurrentGDP times marginal spread-ratio relief"
label variable TA_hat "Marginal tax-base-ratio benefit per readiness-ratio unit"
label variable theta_hat_A "(debt/CurrentGDP)*mA_hat + TA_hat; unified ratio units"
label variable theta_constructible "All row-level theta inputs nonmissing"

* Delta-method standard errors for the two components; a joint theta SE is not
* reported because it requires cross-equation covariance or a full bootstrap.
estimates restore Spread_Quadratic_all
predictnl double __mA_pn = -(_b[c_A] + _b[half_A2]*c_A + _b[int_AB]*c_b + _b[int_AX]*c_X) if !missing(c_A,c_b,c_X), se(mA_hat_se_spread_ratio)
generate double mA_hat_se = mA_hat_se_spread_ratio if !missing(mA_hat_se_spread_ratio)
estimates restore T11_quadratic_full
predictnl double __TA_pn = _b[c_A_T] + _b[half_A2_T]*c_A_T + _b[int_AX_T]*c_X_T if !missing(c_A_T,c_X_T), se(TA_hat_se)

* Algebra and scale checks.
generate double __mA_raw_formula = -(scalar(beta_A_raw) + scalar(beta_AA)*readiness100 + scalar(beta_AB)*b_it_theta + scalar(beta_AX)*vulnerability100) if !missing(readiness100,b_it_theta,vulnerability100)
generate double __mb_centered = scalar(beta_b_centered) + scalar(beta_bb)*c_b + scalar(beta_AB)*c_A + scalar(beta_bX)*c_X if !missing(c_A,c_b,c_X)
generate double __mb_raw = scalar(beta_b_raw) + scalar(beta_bb)*b_it_theta + scalar(beta_AB)*readiness100 + scalar(beta_bX)*vulnerability100 if !missing(readiness100,b_it_theta,vulnerability100)
generate double __mX_centered = scalar(beta_X_centered) + scalar(beta_XX)*c_X + scalar(beta_AX)*c_A + scalar(beta_bX)*c_b if !missing(c_A,c_b,c_X)
generate double __mX_raw = scalar(beta_X_raw) + scalar(beta_XX)*vulnerability100 + scalar(beta_AX)*readiness100 + scalar(beta_bX)*b_it_theta if !missing(readiness100,b_it_theta,vulnerability100)
generate double __TA_raw_formula = scalar(gamma_A_raw) + scalar(gamma_AA)*readiness100 + scalar(gamma_AX)*vulnerability100 if !missing(readiness100,vulnerability100)
generate double __b_mapping_diff = abs(b_it_theta-debt/CurrentGDP) if CurrentGDP>0 & !missing(b_it_theta,debt)
generate double __theta_formula = b_it_theta*mA_hat + TA_hat if !missing(b_it_theta,mA_hat,TA_hat)

tempname p_formula
postfile `p_formula' str48 check double max_abs_diff tolerance byte passed using "`outdir'/formula_checks.dta", replace
quietly summarize __b_mapping_diff, meanonly
post `p_formula' ("b_it equals debt/CurrentGDP exactly") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mA_raw = abs(mA_hat_spread_ratio-__mA_raw_formula)
quietly summarize __diff_mA_raw, meanonly
post `p_formula' ("centered versus raw mA formula") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mb_raw = abs(__mb_centered-__mb_raw)
quietly summarize __diff_mb_raw, meanonly
post `p_formula' ("centered versus raw b derivative") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mX_raw = abs(__mX_centered-__mX_raw)
quietly summarize __diff_mX_raw, meanonly
post `p_formula' ("centered versus raw X derivative") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mA_pn = abs(mA_hat_spread_ratio-__mA_pn)
quietly summarize __diff_mA_pn, meanonly
post `p_formula' ("stored versus predictnl mA") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_TA_raw = abs(TA_hat-__TA_raw_formula)
quietly summarize __diff_TA_raw, meanonly
post `p_formula' ("centered versus raw tax formula") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_TA_pn = abs(TA_hat-__TA_pn)
quietly summarize __diff_TA_pn, meanonly
post `p_formula' ("stored versus predictnl tax margin") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_theta = abs(theta_hat_A-__theta_formula)
quietly summarize __diff_theta, meanonly
post `p_formula' ("theta component identity") (r(max)) (1e-12) (r(max)<=1e-12)
postclose `p_formula'
preserve
    use "`outdir'/formula_checks.dta", clear
    export delimited using "`outdir'/formula_checks.csv", replace
restore

drop __mA_pn __TA_pn __mA_raw_formula __mb_centered __mb_raw __mX_centered __mX_raw __TA_raw_formula __b_mapping_diff __theta_formula __diff_mA_raw __diff_mb_raw __diff_mX_raw __diff_mA_pn __diff_TA_raw __diff_TA_pn __diff_theta

* Descriptive statistics on the appropriate supported samples.
tempname p_desc
postfile `p_desc' str32 variable str24 sample double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/descriptive_stats.dta", replace
foreach v in taxbase_lead taxbase_lag {
    quietly summarize `v' if sample_tax, detail
    post `p_desc' ("`v'") ("tax") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
foreach v in mA_hat_spread_ratio mA_hat spread_saving_component TA_hat theta_hat_A {
    quietly summarize `v' if sample_theta_support, detail
    post `p_desc' ("`v'") ("theta_support") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
quietly summarize theta_hat_A if theta_constructible, detail
post `p_desc' ("theta_hat_A") ("all_constructible") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
postclose `p_desc'
preserve
    use "`outdir'/descriptive_stats.dta", clear
    export delimited using "`outdir'/descriptive_stats.csv", replace
restore

* Observation-level audit and reusable generated panel.
preserve
    keep country_name iso3 country_id year outcome_year duplicate_key sample_spread sample_tax sample_theta_support theta_constructible tax_missing_count taxbase_lead taxbase_lag debt CurrentGDP debt_gdp b_it_theta ln_currentgdp mA_hat_spread_ratio mA_hat mA_hat_se spread_saving_component TA_hat TA_hat_se theta_hat_A
    sort iso3 year
    export delimited using "`outdir'/sample_audit.csv", replace
restore

preserve
    keep country_name iso3 country_id year outcome_year bond_spreads readiness100 vulnerability100 debt_gdp b_it_theta revenue CurrentGDP ln_currentgdp revenue_lead currentgdp_lag taxbase_lead taxbase_lag growth inflation_cpi reserves tt sample_spread sample_tax sample_theta_support theta_constructible mA_hat_spread_ratio mA_hat mA_hat_se spread_saving_component TA_hat TA_hat_se theta_hat_A
    sort iso3 year
    save "`outdir'/empirical_theta_panel.dta", replace
    export delimited using "`outdir'/empirical_theta_panel.csv", replace
restore

quietly count if theta_constructible
scalar N_theta_constructible = r(N)
quietly count if sample_tax & outcome_year!=year+1
scalar N_bad_outcome_alignment = r(N)
quietly count if CurrentGDP>0 & !missing(debt,CurrentGDP) & (missing(b_it_theta) | abs(b_it_theta-debt/CurrentGDP)>1e-12)
scalar N_bad_b_mapping = r(N)

tempname p_meta
postfile `p_meta' str48 item double value using "`outdir'/run_metadata.dta", replace
post `p_meta' ("raw_observations") (scalar(N_raw))
post `p_meta' ("duplicate_country_year_rows") (scalar(N_duplicate_rows))
post `p_meta' ("nonpositive_CurrentGDP_rows") (scalar(N_nonpositive_current_gdp))
post `p_meta' ("spread_sample_observations") (scalar(N_spread))
post `p_meta' ("spread_sample_countries") (scalar(G_spread))
post `p_meta' ("spread_sample_years") (scalar(T_spread))
post `p_meta' ("spread_sample_first_year") (scalar(year_min_spread))
post `p_meta' ("spread_sample_last_year") (scalar(year_max_spread))
post `p_meta' ("tax_sample_observations") (scalar(N_tax))
post `p_meta' ("tax_sample_countries") (scalar(G_tax))
post `p_meta' ("tax_sample_years") (scalar(T_tax))
post `p_meta' ("tax_sample_first_year") (scalar(year_min_tax))
post `p_meta' ("tax_sample_last_year") (scalar(year_max_tax))
post `p_meta' ("theta_support_observations") (scalar(N_theta_support))
post `p_meta' ("theta_support_countries") (scalar(G_theta_support))
post `p_meta' ("theta_support_years") (scalar(T_theta_support))
post `p_meta' ("theta_constructible_observations") (scalar(N_theta_constructible))
post `p_meta' ("bad_outcome_year_alignment_rows") (scalar(N_bad_outcome_alignment))
post `p_meta' ("bad_b_it_debt_CurrentGDP_mapping_rows") (scalar(N_bad_b_mapping))
postclose `p_meta'
preserve
    use "`outdir'/run_metadata.dta", clear
    export delimited using "`outdir'/run_metadata.csv", replace
restore

display as result "ANALYSIS COMPLETE. Tax sample N=" scalar(N_tax) ", countries=" scalar(G_tax) ", years=" scalar(T_tax)
display as result "Theta support N=" scalar(N_theta_support) "; constructible rows=" scalar(N_theta_constructible)
display as result "All results written to `outdir'."
log close mainlog
exit, clear
