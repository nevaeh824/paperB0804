version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* -----------------------------------------------------------------------------
* Empirical adaptation-capacity theta workflow.
*
* 1. Reproduce the baseline full-interaction sovereign-spread model.
* 2. Estimate the one-period-ahead constant-GDP-level-ratio T equation.
* 3. Construct marginal spread relief, marginal T benefit, and theta.
*
* The source CSV is read only. No row is deleted, no variable is winsorized, and
* every regression uses the complete cases for its current variables.
* The formal Section-3 regressions use LSDVC with a Blundell--Bond initializer,
* second-order bias correction, and 50 bootstrap replications. Country effects
* are implicit in LSDVC and explicit year dummies supply year fixed effects.
* -----------------------------------------------------------------------------

args project resultroot
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0804"
if "`resultroot'"=="" local resultroot "`project'/paperB/paperBresult"
local datadir     "`project'/data0804"
local wsdifile    "`project'/WSDI/data/processed/wsdi_sovereign61_1995_2018.csv"
local baselinedir "`resultroot'/baseline/stata_outputs"
local workflowdir "`resultroot'/empirical_theta"
local outdir      "`workflowdir'/stata_outputs"

capture mkdir "`workflowdir'"
capture mkdir "`outdir'"
capture log close _all
log using "`outdir'/empirical_theta.log", text replace name(mainlog)

display as text "ANALYSIS START: `c(current_date)' `c(current_time)'"
display as text "SOURCE: `datadir'/invest_panel_weo.csv"
display as text "WSDI SOURCE: `wsdifile'"
display as text "BASELINE SOURCE: `baselinedir'/model_coefficients.csv"
display as text "POLICY: source preserved; exact panel time operators; current-variable complete cases; no silent deletion."

import delimited using "`datadir'/invest_panel_weo.csv", clear varnames(1) case(preserve) encoding(UTF-8)
compress
count
scalar N_raw = r(N)

* Merge WSDI by the unique sovereign-year key while preserving every main-panel
* row. The old vulnerability source field is not used as theoretical X.
tempfile wsdi_source
preserve
    import delimited using "`wsdifile'", clear varnames(1) case(preserve) encoding(UTF-8) asdouble
    foreach v in iso3 year wsdi_days {
        confirm variable `v'
    }
    keep iso3 year wsdi_days
    count
    scalar N_wsdi_source_rows = r(N)
    quietly count if !missing(wsdi_days)
    scalar N_wsdi_source_nonmissing = r(N)
    duplicates tag iso3 year, generate(wsdi_duplicate_key)
    quietly count if wsdi_duplicate_key>0
    scalar N_wsdi_duplicate_rows = r(N)
    export delimited iso3 year wsdi_days wsdi_duplicate_key if wsdi_duplicate_key>0 using "`outdir'/wsdi_duplicate_country_year.csv", replace
    drop wsdi_duplicate_key
    save `wsdi_source', replace
restore
if scalar(N_wsdi_duplicate_rows)>0 {
    display as error "Duplicate WSDI iso3-year keys exist. Workflow stopped."
    log close mainlog
    exit 459
}
merge m:1 iso3 year using `wsdi_source', keep(master match) keepusing(wsdi_days) generate(wsdi_merge)
quietly count if wsdi_merge==3
scalar N_wsdi_matched_rows = r(N)
quietly count if wsdi_merge==1
scalar N_wsdi_unmatched_master_rows = r(N)
capture drop vulnerability100 vulnerability_delta100

* Unified regression-unit convention inherited from baseline: all source rates,
* percentages, and 0--100 indices enter as 0--1 ratios. GDP and other monetary
* amounts stay in their source units. Variable names are retained for downstream
* compatibility, and an explicit audit records every conversion.
local ratio_vars bond_spreads bond_10y readiness100 growth inflation_cpi debt_gdp PrimaryBalance_gdp reserves tt Revenue_gdp OverallBalance_gdp interest_revenue
tempname p_units
postfile `p_units' str32 variable double source_min source_max ratio_min ratio_max max_abs_scaling_diff byte passed using "`outdir'/unit_scaling_checks.dta", replace
recast double wsdi_days
generate double __wsdi_source_value = wsdi_days
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
quietly summarize __wsdi_source_value, meanonly
scalar __wsdi_source_min = r(min)
scalar __wsdi_source_max = r(max)
replace wsdi_days = __wsdi_source_value*0.01
generate double __wsdi_scale_diff = abs(wsdi_days-__wsdi_source_value*0.01) if !missing(__wsdi_source_value)
quietly summarize __wsdi_scale_diff, meanonly
scalar __wsdi_max_diff = cond(r(N)>0,r(max),0)
quietly summarize wsdi_days, meanonly
post `p_units' ("wsdi_days") (scalar(__wsdi_source_min)) (scalar(__wsdi_source_max)) (r(min)) (r(max)) (scalar(__wsdi_max_diff)) (scalar(__wsdi_max_diff)<=1e-12)
drop __wsdi_source_value __wsdi_scale_diff
postclose `p_units'
preserve
    use "`outdir'/unit_scaling_checks.dta", clear
    format source_min source_max ratio_min ratio_max max_abs_scaling_diff %21.15g
    export delimited using "`outdir'/unit_scaling_checks.csv", replace datafmt
restore

label variable bond_spreads "Sovereign spread ratio; source percentage divided by 100"
label variable bond_10y "Ten-year yield ratio; source percentage divided by 100"
label variable wsdi_days "WSDI days scaled by 0.01; theoretical X"
label variable readiness100 "ND-GAIN readiness ratio; source index divided by 100"
label variable debt_gdp "Government debt/GDP ratio; source percentage divided by 100"
label variable growth "Real GDP growth ratio; source percentage divided by 100"
label variable inflation_cpi "CPI inflation ratio; source percentage divided by 100"
label variable interest_revenue "Interest/revenue ratio; source percentage divided by 100"

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
quietly tabulate year, generate(__year_fe_)
ds __year_fe_*
local year_dummies `r(varlist)'
local base_year_dummy : word 1 of `year_dummies'
local year_dummies : list year_dummies - base_year_dummy
generate double spread_lag = L.bond_spreads
label variable spread_lag "Sovereign spread ratio at t-1; exact panel lag"
generate double b_it = debt_gdp
label variable b_it "Contemporaneous debt/GDP ratio b(t)"

* Baseline transformation and exact time-aligned T indicator.
quietly count if ConstantGDP<=0 & !missing(ConstantGDP)
scalar N_nonpositive_constant_gdp = r(N)
assert scalar(N_nonpositive_constant_gdp)==0
generate double ln_constantgdp = ln(ConstantGDP) if ConstantGDP>0

generate double ln_constantgdp_lag = L.ln_constantgdp
generate double T_it = ConstantGDP/L.ConstantGDP if !missing(ConstantGDP,L.ConstantGDP) & L.ConstantGDP!=0
generate double T_lead = F.T_it
generate int outcome_year = year + 1 if !missing(T_lead)
generate double b_outcome_common = F.debt_gdp-debt_gdp if !missing(F.debt_gdp,debt_gdp)
generate double A_outcome_common = readiness100-L.readiness100 if !missing(readiness100,L.readiness100)

label variable ln_constantgdp_lag "Natural log of ConstantGDP at t-1; exact panel lag"
label variable T_it "T(t): ConstantGDP_t divided by ConstantGDP_t-1"
label variable T_lead "T(t+1): exact panel lead of T(t)"
label variable outcome_year "Calendar year of T(t+1)"

* Define complete cases for the two preferred upstream equations. These flags
* support diagnostics and centering only; progressive models use their own RHS.
local spread_controls growth inflation_cpi reserves tt
local spread_modelvars bond_spreads wsdi_days readiness100 b_it spread_lag `spread_controls'
egen int spread_missing_count = rowmiss(`spread_modelvars')
generate byte eligible_spread = (spread_missing_count==0)
label variable eligible_spread "Nonmissing eligibility for sovereign-spread full model"
generate byte sample_spread = eligible_spread
label variable sample_spread "Complete cases for Spread_Interact_all"

* The T equation excludes GDP levels and logs as separate controls. ConstantGDP
* is used only through the defined consecutive-level ratio T(t).
local tax_controls inflation_cpi reserves tt
local tax_modelvars T_lead readiness100 wsdi_days T_it `tax_controls'
egen int tax_missing_count = rowmiss(`tax_modelvars')
generate byte eligible_tax = (tax_missing_count==0)
label variable eligible_tax "Nonmissing eligibility for T-indicator full model"
generate byte sample_tax = eligible_tax
label variable sample_tax "Complete cases for T10_interact_full"

* Sample counts and coverage.
foreach s in spread tax {
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
local tax_profilevars T_lead T_it readiness100 wsdi_days inflation_cpi reserves tt

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

local tax_corrvars readiness100 wsdi_days T_it inflation_cpi reserves tt
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

* Center interacting variables within the complete cases of the corresponding
* preferred interaction equation. The flags do not constrain progressive runs.
tempname p_center
postfile `p_center' str16 sample str32 variable double mean sd min p10 p25 p50 p75 p90 max using "`outdir'/centering.dta", replace

foreach v in readiness100 b_it wsdi_days {
    quietly summarize `v' if sample_spread, detail
    scalar spread_mean_`v' = r(mean)
    scalar spread_sd_`v' = r(sd)
    post `p_center' ("spread") ("`v'") (r(mean)) (r(sd)) (r(min)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90)) (r(max))
}
foreach v in readiness100 wsdi_days {
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
generate double c_b = b_it - scalar(spread_mean_b_it)
generate double c_X = wsdi_days - scalar(spread_mean_wsdi_days)
generate double int_AB = c_A*c_b
generate double int_AX = c_A*c_X

generate double c_A_T = readiness100 - scalar(tax_mean_readiness100)
generate double c_X_T = wsdi_days - scalar(tax_mean_wsdi_days)
generate double int_AX_T = c_A_T*c_X_T

label variable c_A "readiness100 centered on spread sample"
label variable c_b "contemporaneous debt/GDP b_it centered on spread sample"
label variable c_X "wsdi_days centered on spread sample"
label variable int_AB "c_A times c_b"
label variable int_AX "c_A times c_X"
label variable c_A_T "readiness100 centered on tax sample"
label variable c_X_T "wsdi_days centered on tax sample"
label variable int_AX_T "c_A_T times c_X_T"

preserve
    use "`outdir'/centering.dta", clear
    export delimited using "`outdir'/centering.csv", replace
restore

* VIF after removing country and year fixed effects, for the full linear and
* full interaction specifications separately.
local vif_linear readiness100 wsdi_days T_it inflation_cpi reserves tt
local vif_interaction c_A_T c_X_T int_AX_T T_it inflation_cpi reserves tt
local vif_all : list vif_linear | vif_interaction
foreach v of local vif_all {
    quietly regress `v' i.country_id i.year if sample_tax
    predict double tw_`v' if sample_tax, residuals
}
tempname p_vif
postfile `p_vif' str24 specification str32 variable double vif tolerance condition_number using "`outdir'/collinearity.dta", replace
foreach spec in linear interaction {
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
postfile `p_models' str28 model double N countries years first_year last_year r2_within r2_overall clusters df_r str16 cluster_variable byte country_fe year_fe macro_controls external_controls interaction str12 estimator str20 initial_estimator double bias_order bootstrap_reps str16 se_type str32 dynamic_lag using "`outdir'/model_stats.dta", replace
postfile `p_coefs' str28 model str32 variable double coefficient se t p ci_low ci_high byte omitted using "`outdir'/model_coefficients.dta", replace
postfile `p_equations' str28 model str244 equation using "`outdir'/equations.dta", replace
postfile `p_construct' str20 source str32 parameter double estimate se t p ci_low ci_high str48 units using "`outdir'/construction_coefficients.dta", replace

* -----------------------------------------------------------------------------
* Baseline full interaction, reproduced on its current-variable complete cases.
* -----------------------------------------------------------------------------
local spread_rhs c_A c_X c_b int_AB int_AX growth inflation_cpi reserves tt
set seed 20260818
quietly xtlsdvc bond_spreads `spread_rhs' `year_dummies', initial(bb) bias(2) vcov(50)
estimates store Spread_Interact_all
assert e(sample)==1 if sample_spread
quietly count if sample_spread
assert r(N)==e(N)
quietly levelsof country_id if sample_spread, local(__spread_countries)
local __spread_ng : word count `__spread_countries'
quietly levelsof year if sample_spread, local(__spread_years)
local __spread_nt : word count `__spread_years'
quietly summarize year if sample_spread, meanonly
post `p_models' ("Spread_Interact_all") (e(N)) (`__spread_ng') (`__spread_nt') (r(min)) (r(max)) (.) (.) (.) (.) ("") (1) (1) (1) (1) (1) ("LSDVC") ("Blundell-Bond") (2) (50) ("bootstrap") ("L.bond_spreads")
post `p_equations' ("Spread_Interact_all") ("s_it = FE_i + FE_t + rho_s s_i,t-1 + beta_A A_c + beta_X X_c + beta_B b_c + beta_AB(A_c*b_c) + beta_AX(A_c*X_c) + controls + error")

local spread_report_rhs "`spread_rhs' spread_lag"
foreach v of local spread_report_rhs {
    local bname "`v'"
    if "`v'"=="spread_lag" local bname "L.bond_spreads"
    capture scalar __b = _b[`bname']
    if _rc {
        post `p_coefs' ("Spread_Interact_all") ("`v'") (.) (.) (.) (.) (.) (.) (1)
    }
    else {
        scalar __se = _se[`bname']
        scalar __t = cond(__se>0,__b/__se,.)
        scalar __p = cond(__se>0,2*normal(-abs(__t)),.)
        scalar __crit = invnormal(.975)
        post `p_coefs' ("Spread_Interact_all") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
    }
}

scalar beta_A_centered = _b[c_A]
scalar beta_AB = _b[int_AB]
scalar beta_AX = _b[int_AX]
scalar beta_A_raw = scalar(beta_A_centered) - scalar(beta_AB)*scalar(spread_mean_b_it) - scalar(beta_AX)*scalar(spread_mean_wsdi_days)

quietly lincom c_A - scalar(spread_mean_b_it)*int_AB - scalar(spread_mean_wsdi_days)*int_AX
post `p_construct' ("spread") ("beta_A_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per A-ratio unit")
quietly lincom int_AB
post `p_construct' ("spread") ("beta_AB") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per A-ratio per debt-ratio unit")
quietly lincom int_AX
post `p_construct' ("spread") ("beta_AX") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("spread ratio per A-ratio per X-ratio unit")

* -----------------------------------------------------------------------------
* Ten T-indicator models on their own current-variable samples. Models 1--7 reproduce the
* baseline progression; Models 8--10 test the A-by-X interaction as controls are
* added sequentially. Every interaction model retains both lower-order terms.
* -----------------------------------------------------------------------------
local tm1  "T1_X_only"
local tr1  "wsdi_days"
local tq1  "T(t+1) = FE_i + FE_t + rho_T T(t) + gamma_X X_it + error"
local mc1  0
local ec1  0
local ix1  0

local tm2  "T2_A_only"
local tr2  "readiness100"
local tq2  "T(t+1) = FE_i + FE_t + rho_T T(t) + gamma_A A_it + error"
local mc2  0
local ec2  0
local ix2  0

local tm3  "T3_persistence"
local tr3  ""
local tq3  "T(t+1) = FE_i + FE_t + rho_T T(t) + error"
local mc3  0
local ec3  0
local ix3  0

local tm4  "T4_all_core"
local tr4  "wsdi_days readiness100"
local tq4  "T(t+1) = FE_i + FE_t + gamma_X X_it + gamma_A A_it + rho_T T(t) + error"
local mc4  0
local ec4  0
local ix4  0

local tm5  "T5_macro"
local tr5  "wsdi_days readiness100 inflation_cpi"
local tq5  "T(t+1) = FE_i + FE_t + core + inflation + error; GDP controls and growth excluded"
local mc5  1
local ec5  0
local ix5  0

local tm6  "T6_layer1_X"
local tr6  "wsdi_days inflation_cpi reserves tt"
local tq6  "T(t+1) = FE_i + FE_t + gamma_X X_it + rho_T T(t) + Gamma W + error"
local mc6  1
local ec6  1
local ix6  0

local tm7  "T7_layer2_A"
local tr7  "wsdi_days readiness100 inflation_cpi reserves tt"
local tq7  "T(t+1) = FE_i + FE_t + gamma_A A_it + gamma_X X_it + rho_T T(t) + Gamma W + error"
local mc7  1
local ec7  1
local ix7  0

local tm8  "T8_interact_core"
local tr8  "c_A_T c_X_T int_AX_T"
local tq8  "T(t+1) = FE_i + FE_t + gamma_A A_c + gamma_X X_c + gamma_AX(A_c*X_c) + rho_T T(t) + error"
local mc8  0
local ec8  0
local ix8  1

local tm9  "T9_interact_macro"
local tr9  "c_A_T c_X_T int_AX_T inflation_cpi"
local tq9  "T(t+1) = FE_i + FE_t + centered interaction core + inflation + error; GDP controls and growth excluded"
local mc9  1
local ec9  0
local ix9  1

local tm10 "T10_interact_full"
local tr10 "c_A_T c_X_T int_AX_T inflation_cpi reserves tt"
local tq10 "T(t+1) = FE_i + FE_t + centered interaction core + Gamma W + error; current GDP excluded"
local mc10 1
local ec10 1
local ix10 1

forvalues z=1/10 {
    local mid "`tm`z''"
    local rhs "`tr`z''"
    local equ "`tq`z''"
    display as text "T-INDICATOR REGRESSION `mid': `equ'"
    set seed 20260818
    quietly xtlsdvc T_lead `rhs' `year_dummies', initial(bb) bias(2) vcov(50)
    estimates store `mid'
    capture drop __model_missing __model_sample
    egen int __model_missing = rowmiss(T_lead T_it `rhs')
    generate byte __model_sample = e(sample) & __model_missing==0
    quietly count if __model_sample
    assert r(N)==e(N)
    if `z'==10 {
        assert __model_sample==sample_tax
    }
    quietly levelsof country_id if __model_sample, local(__countries)
    local __ng : word count `__countries'
    quietly levelsof year if __model_sample, local(__years)
    local __nt : word count `__years'
    quietly summarize year if __model_sample, meanonly
    post `p_models' ("`mid'") (e(N)) (`__ng') (`__nt') (r(min)) (r(max)) (.) (.) (.) (.) ("") (1) (1) (`mc`z'') (`ec`z'') (`ix`z'') ("LSDVC") ("Blundell-Bond") (2) (50) ("bootstrap") ("L.T_lead")
    post `p_equations' ("`mid'") ("`equ'")
    local report_rhs "`rhs' T_it"
    foreach v of local report_rhs {
        local bname "`v'"
        if "`v'"=="T_it" local bname "L.T_lead"
        capture scalar __b = _b[`bname']
        if _rc {
            post `p_coefs' ("`mid'") ("`v'") (.) (.) (.) (.) (.) (.) (1)
        }
        else {
            scalar __se = _se[`bname']
            scalar __t = cond(__se>0,__b/__se,.)
            scalar __p = cond(__se>0,2*normal(-abs(__t)),.)
            scalar __crit = invnormal(.975)
            post `p_coefs' ("`mid'") ("`v'") (__b) (__se) (__t) (__p) (__b-__crit*__se) (__b+__crit*__se) (__se==0)
        }
    }
}

* Preferred T-indicator coefficients are from Model 10, with all specified
* controls and no GDP level/log regressor beyond the construction of T itself.
estimates restore T10_interact_full
scalar gamma_A_centered = _b[c_A_T]
scalar gamma_AX = _b[int_AX_T]
scalar gamma_A_raw = scalar(gamma_A_centered) - scalar(gamma_AX)*scalar(tax_mean_wsdi_days)

quietly lincom c_A_T - scalar(tax_mean_wsdi_days)*int_AX_T
post `p_construct' ("T") ("gamma_A_raw") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("constant-GDP level ratio per A-ratio unit")
quietly lincom int_AX_T
post `p_construct' ("T") ("gamma_AX") (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub)) ("constant-GDP level ratio per A-ratio per X-ratio")

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
foreach v in wsdi_days readiness100 T_it {
    local bname "`v'"
    if "`v'"=="T_it" local bname "L.T_lead"
    scalar base_linear_`v' = _b[`bname']
}
foreach mid in T5_macro T7_layer2_A {
    estimates restore `mid'
    foreach v in wsdi_days readiness100 T_it {
        local bname "`v'"
        if "`v'"=="T_it" local bname "L.T_lead"
        scalar __new = _b[`bname']
        scalar __change = __new-scalar(base_linear_`v')
        if abs(scalar(base_linear_`v'))<1e-8 post `p_changes' ("T4_all_core") ("`mid'") ("`v'") (scalar(base_linear_`v')) (__new) (__change) (.) ("absolute; near zero")
        else post `p_changes' ("T4_all_core") ("`mid'") ("`v'") (scalar(base_linear_`v')) (__new) (__change) (100*__change/abs(scalar(base_linear_`v'))) ("percent")
    }
}
estimates restore T8_interact_core
foreach v in c_A_T c_X_T int_AX_T T_it {
    local bname "`v'"
    if "`v'"=="T_it" local bname "L.T_lead"
    scalar base_interaction_`v' = _b[`bname']
}
foreach mid in T9_interact_macro T10_interact_full {
    estimates restore `mid'
    foreach v in c_A_T c_X_T int_AX_T T_it {
        local bname "`v'"
        if "`v'"=="T_it" local bname "L.T_lead"
        scalar __new = _b[`bname']
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
quietly test inflation_cpi
post `p_wald' ("T5_macro") ("macro controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
estimates restore T7_layer2_A
quietly test reserves tt
post `p_wald' ("T7_layer2_A") ("external controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
quietly test inflation_cpi reserves tt
post `p_wald' ("T7_layer2_A") ("all controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
foreach mid in T8_interact_core T9_interact_macro T10_interact_full {
    estimates restore `mid'
    quietly test c_A_T int_AX_T
    post `p_wald' ("`mid'") ("adaptation terms jointly zero: c_A_T = int_AX_T = 0") (r(chi2)) (r(df)) (.) (r(p))
    quietly test int_AX_T
    post `p_wald' ("`mid'") ("interaction zero: int_AX_T = 0") (r(chi2)) (r(df)) (.) (r(p))
}
estimates restore T9_interact_macro
quietly test inflation_cpi
post `p_wald' ("T9_interact_macro") ("macro controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
estimates restore T10_interact_full
quietly test reserves tt
post `p_wald' ("T10_interact_full") ("external controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
quietly test inflation_cpi reserves tt
post `p_wald' ("T10_interact_full") ("all controls jointly zero") (r(chi2)) (r(df)) (.) (r(p))
postclose `p_wald'
preserve
    use "`outdir'/wald_tests.dta", clear
    export delimited using "`outdir'/wald_tests.csv", replace
restore

* Delta-method marginal T benefits across the observed X distribution.
tempname p_marginal p_threshold
postfile `p_marginal' str28 model str24 moderator str20 point double moderator_value marginal_effect se t p ci_low ci_high using "`outdir'/marginal_effects.dta", replace
postfile `p_threshold' str28 model str24 moderator double threshold sample_min sample_max byte in_range using "`outdir'/thresholds.dta", replace
foreach mid in T8_interact_core T9_interact_macro T10_interact_full {
    estimates restore `mid'
    local xmean = scalar(tax_mean_wsdi_days)
    local xsd = scalar(tax_sd_wsdi_days)
    local pnames "P10 P25 P50 P75 P90 Mean_minus_1SD Mean Mean_plus_1SD"
    local pvals "`=scalar(tax_p10_wsdi_days)' `=scalar(tax_p25_wsdi_days)' `=scalar(tax_p50_wsdi_days)' `=scalar(tax_p75_wsdi_days)' `=scalar(tax_p90_wsdi_days)' `=`xmean'-`xsd'' `xmean' `=`xmean'+`xsd''"
    forvalues h=1/8 {
        local pn : word `h' of `pnames'
        local pv : word `h' of `pvals'
        local centered = `pv'-`xmean'
        quietly lincom c_A_T + (`centered')*int_AX_T
        post `p_marginal' ("`mid'") ("wsdi_days") ("`pn'") (`pv') (r(estimate)) (r(se)) (r(estimate)/r(se)) (r(p)) (r(lb)) (r(ub))
    }
    scalar __threshold = `xmean' - _b[c_A_T]/_b[int_AX_T]
    scalar __inrange = (__threshold>=scalar(tax_min_wsdi_days) & __threshold<=scalar(tax_max_wsdi_days))
    post `p_threshold' ("`mid'") ("wsdi_days") (__threshold) (scalar(tax_min_wsdi_days)) (scalar(tax_max_wsdi_days)) (__inrange)
}
postclose `p_marginal'
postclose `p_threshold'
foreach f in marginal_effects thresholds {
    preserve
        use "`outdir'/`f'.dta", clear
        export delimited using "`outdir'/`f'.csv", replace
    restore
}

* -----------------------------------------------------------------------------
* Validate reproduced spread coefficients against baseline's saved results.
* -----------------------------------------------------------------------------
estimates restore Spread_Interact_all
foreach v in c_A c_X c_b int_AB int_AX spread_lag growth inflation_cpi reserves tt {
    local bname "`v'"
    if "`v'"=="spread_lag" local bname "L.bond_spreads"
    scalar main_spread_`v' = _b[`bname']
    scalar main_spread_se_`v' = _se[`bname']
}

tempname p_baseline_validation
postfile `p_baseline_validation' str32 variable double reproduced_b baseline_b abs_b_diff reproduced_se baseline_se abs_se_diff using "`outdir'/baseline_validation.dta", replace
preserve
    use "`baselinedir'/model_coefficients.dta", clear
    foreach v in c_A c_X c_b int_AB int_AX spread_lag growth inflation_cpi reserves tt {
        quietly summarize coefficient if model=="Interact_all" & variable=="`v'", meanonly
        if r(N)!=1 {
            display as error "Expected exactly one baseline coefficient for `v'; found " r(N)
            restore
            log close mainlog
            exit 459
        }
        scalar __base_b = r(mean)
        quietly summarize se if model=="Interact_all" & variable=="`v'", meanonly
        scalar __base_se = r(mean)
        post `p_baseline_validation' ("`v'") (scalar(main_spread_`v')) (scalar(__base_b)) (abs(scalar(main_spread_`v')-scalar(__base_b))) (scalar(main_spread_se_`v')) (scalar(__base_se)) (abs(scalar(main_spread_se_`v')-scalar(__base_se)))
    }
restore
postclose `p_baseline_validation'
preserve
    use "`outdir'/baseline_validation.dta", clear
    quietly summarize abs_b_diff, meanonly
    display as text "MAX BASELINE COEFFICIENT REPRODUCTION DIFF: " %21.15g r(max)
    assert r(N)>0 & r(max)<=1e-10
    quietly summarize abs_se_diff, meanonly
    display as text "MAX BASELINE SE REPRODUCTION DIFF: " %21.15g r(max)
    assert r(N)>0 & r(max)<=1e-8
    export delimited using "`outdir'/baseline_validation.csv", replace
restore

* Estimator-configuration audit for the three preferred Section-3 models.
tempname p_estimator_validation
postfile `p_estimator_validation' str28 model str40 check double expected actual byte passed using "`outdir'/estimator_validation.dta", replace
foreach model in Spread_Interact_all T7_layer2_A T10_interact_full {
    estimates restore `model'
    post `p_estimator_validation' ("`model'") ("e(cmd) is xtlsdvc") (1) ("`e(cmd)'"=="xtlsdvc") ("`e(cmd)'"=="xtlsdvc")
    if "`model'"=="Spread_Interact_all" local audit_var "int_AB"
    if "`model'"=="T7_layer2_A" local audit_var "wsdi_days"
    if "`model'"=="T10_interact_full" local audit_var "int_AX_T"
    scalar __positive_v = (_se[`audit_var']>0 & !missing(_se[`audit_var']))
    post `p_estimator_validation' ("`model'") ("bootstrap variances positive") (1) (scalar(__positive_v)) (scalar(__positive_v)==1)
}
postclose `p_estimator_validation'
preserve
    use "`outdir'/estimator_validation.dta", clear
    export delimited using "`outdir'/estimator_validation.csv", replace
restore

* -----------------------------------------------------------------------------
* Row-level construction is restricted to each preferred source regression's
* verified e(sample). Coefficients are not extrapolated to rows excluded from
* the equation that estimated them.
* -----------------------------------------------------------------------------
generate double mA_hat_spread_ratio = -(scalar(beta_A_centered) + scalar(beta_AB)*c_b + scalar(beta_AX)*c_X) if sample_spread
generate double mA_hat = mA_hat_spread_ratio if sample_spread
generate double spread_saving_component = b_it*mA_hat if !missing(b_it,mA_hat)
generate double TA_hat = scalar(gamma_A_centered) + scalar(gamma_AX)*c_X_T if sample_tax
generate double theta_hat_A = spread_saving_component + TA_hat if !missing(b_it,mA_hat,TA_hat)
generate byte theta_constructible = !missing(b_it,mA_hat,TA_hat,theta_hat_A)
generate byte sample_theta_support = theta_constructible
label variable sample_theta_support "Intersection of preferred source regression samples supporting theta"
assert !missing(mA_hat)==sample_spread
assert !missing(TA_hat)==sample_tax
assert !missing(theta_hat_A) == (!missing(b_it) & !missing(mA_hat) & !missing(TA_hat))
assert sample_theta_support == (sample_spread & sample_tax & !missing(b_it))

quietly count if sample_theta_support
scalar N_theta_support = r(N)
egen byte tag_country_theta_support = tag(country_id) if sample_theta_support
egen byte tag_year_theta_support = tag(year) if sample_theta_support
quietly count if tag_country_theta_support==1
scalar G_theta_support = r(N)
quietly count if tag_year_theta_support==1
scalar T_theta_support = r(N)

label variable mA_hat_spread_ratio "Marginal spread-ratio relief per readiness-ratio unit"
label variable mA_hat "Marginal spread-ratio relief from baseline full-interaction model"
label variable spread_saving_component "Contemporaneous debt/GDP ratio times marginal spread-ratio relief"
label variable TA_hat "Marginal T-indicator benefit per readiness-ratio unit"
label variable theta_hat_A "b_it*mA_hat + TA_hat; unified ratio units"
label variable theta_constructible "All row-level theta inputs nonmissing"

* Delta-method standard errors for the two components; a joint theta SE is not
* reported because it requires cross-equation covariance or a full bootstrap.
estimates restore Spread_Interact_all
predictnl double __mA_pn = -(_b[c_A] + _b[int_AB]*c_b + _b[int_AX]*c_X) if sample_spread, se(mA_hat_se_spread_ratio)
generate double mA_hat_se = mA_hat_se_spread_ratio if sample_spread
estimates restore T10_interact_full
predictnl double __TA_pn = _b[c_A_T] + _b[int_AX_T]*c_X_T if sample_tax, se(TA_hat_se)

* Algebra and scale checks.
xtset country_id year
generate double __mA_raw_formula = -(scalar(beta_A_raw) + scalar(beta_AB)*b_it + scalar(beta_AX)*wsdi_days) if sample_spread
generate double __TA_raw_formula = scalar(gamma_A_raw) + scalar(gamma_AX)*wsdi_days if sample_tax
generate double __b_mapping_diff = abs(b_it-debt_gdp) if !missing(b_it,debt_gdp)
generate double __theta_formula = b_it*mA_hat + TA_hat if !missing(b_it,mA_hat,TA_hat)

tempname p_formula
postfile `p_formula' str48 check double max_abs_diff tolerance byte passed using "`outdir'/formula_checks.dta", replace
generate double __T_lead_formula = F.T_it if !missing(F.T_it)
generate double __diff_T_lead = abs(T_lead-__T_lead_formula)
quietly summarize __diff_T_lead, meanonly
post `p_formula' ("T(t+1) equals exact F.T(t)") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __T_it_formula = ConstantGDP/L.ConstantGDP if !missing(ConstantGDP,L.ConstantGDP) & L.ConstantGDP!=0
generate double __diff_T_it = abs(T_it-__T_it_formula)
quietly summarize __diff_T_it, meanonly
post `p_formula' ("T(t) equals ConstantGDP(t) / ConstantGDP(t-1)") (r(max)) (1e-12) (r(max)<=1e-12)
quietly summarize __b_mapping_diff, meanonly
post `p_formula' ("b_it equals contemporaneous debt_gdp") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mA_raw = abs(mA_hat_spread_ratio-__mA_raw_formula)
quietly summarize __diff_mA_raw, meanonly
post `p_formula' ("centered versus raw mA formula") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_mA_pn = abs(mA_hat_spread_ratio-__mA_pn)
quietly summarize __diff_mA_pn, meanonly
post `p_formula' ("stored versus predictnl mA") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_TA_raw = abs(TA_hat-__TA_raw_formula)
quietly summarize __diff_TA_raw, meanonly
post `p_formula' ("centered versus raw T-margin formula") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_TA_pn = abs(TA_hat-__TA_pn)
quietly summarize __diff_TA_pn, meanonly
post `p_formula' ("stored versus predictnl T margin") (r(max)) (1e-12) (r(max)<=1e-12)
generate double __diff_theta = abs(theta_hat_A-__theta_formula)
quietly summarize __diff_theta, meanonly
post `p_formula' ("theta component identity") (r(max)) (1e-12) (r(max)<=1e-12)
postclose `p_formula'
preserve
    use "`outdir'/formula_checks.dta", clear
    export delimited using "`outdir'/formula_checks.csv", replace
restore

quietly count if __b_mapping_diff>1e-12 & !missing(__b_mapping_diff)
scalar N_bad_b_mapping = r(N)
drop __mA_pn __TA_pn __mA_raw_formula __TA_raw_formula __b_mapping_diff __theta_formula __diff_mA_raw __diff_mA_pn __diff_TA_raw __diff_TA_pn __diff_theta __T_lead_formula __diff_T_lead __T_it_formula __diff_T_it

* Descriptive statistics on the appropriate supported samples.
tempname p_desc
postfile `p_desc' str32 variable str24 sample double N mean sd min p10 p25 p50 p75 p90 max using "`outdir'/descriptive_stats.dta", replace
foreach v in T_lead T_it {
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
    keep country_name iso3 country_id year outcome_year duplicate_key wsdi_merge eligible_spread eligible_tax sample_spread sample_tax sample_theta_support theta_constructible spread_missing_count tax_missing_count CurrentGDP ConstantGDP ln_constantgdp ln_constantgdp_lag T_it T_lead b_outcome_common A_outcome_common interest_revenue readiness100 debt_gdp b_it bond_spreads spread_lag wsdi_days mA_hat_spread_ratio mA_hat mA_hat_se spread_saving_component TA_hat TA_hat_se theta_hat_A
    sort iso3 year
    export delimited using "`outdir'/sample_audit.csv", replace
restore

preserve
    keep country_name iso3 country_id year outcome_year bond_spreads spread_lag readiness100 wsdi_days debt_gdp b_it revenue CurrentGDP ConstantGDP ln_constantgdp ln_constantgdp_lag T_it T_lead b_outcome_common A_outcome_common interest_revenue growth inflation_cpi reserves tt wsdi_merge eligible_spread eligible_tax sample_spread sample_tax sample_theta_support theta_constructible mA_hat_spread_ratio mA_hat mA_hat_se spread_saving_component TA_hat TA_hat_se theta_hat_A
    sort iso3 year
    save "`outdir'/empirical_theta_panel.dta", replace
    export delimited using "`outdir'/empirical_theta_panel.csv", replace
restore

quietly count if theta_constructible
scalar N_theta_constructible = r(N)
quietly count if sample_tax & outcome_year!=year+1
scalar N_bad_outcome_alignment = r(N)

tempname p_meta
postfile `p_meta' str48 item double value using "`outdir'/run_metadata.dta", replace
post `p_meta' ("raw_observations") (scalar(N_raw))
post `p_meta' ("duplicate_country_year_rows") (scalar(N_duplicate_rows))
post `p_meta' ("wsdi_source_rows") (scalar(N_wsdi_source_rows))
post `p_meta' ("wsdi_source_nonmissing_rows") (scalar(N_wsdi_source_nonmissing))
post `p_meta' ("wsdi_duplicate_country_year_rows") (scalar(N_wsdi_duplicate_rows))
post `p_meta' ("wsdi_matched_rows") (scalar(N_wsdi_matched_rows))
post `p_meta' ("wsdi_unmatched_master_rows") (scalar(N_wsdi_unmatched_master_rows))
post `p_meta' ("nonpositive_ConstantGDP_rows") (scalar(N_nonpositive_constant_gdp))
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
post `p_meta' ("bad_b_it_current_mapping_rows") (scalar(N_bad_b_mapping))
postclose `p_meta'
preserve
    use "`outdir'/run_metadata.dta", clear
    export delimited using "`outdir'/run_metadata.csv", replace
restore

display as result "ANALYSIS COMPLETE. T-indicator sample N=" scalar(N_tax) ", countries=" scalar(G_tax) ", years=" scalar(T_tax)
display as result "Theta support N=" scalar(N_theta_support) "; constructible rows=" scalar(N_theta_constructible)
display as result "All results written to `outdir'."
log close mainlog
exit, clear
