version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* Paired outer country-block bootstrap for the two debt-timing specifications.
* Each draw re-estimates the point-estimate path required for theta and the final
* kink equation. The formal main-pipeline vcov(50) is intentionally not nested.
args project drawsfile outroot reps
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0805"
if "`drawsfile'"=="" local drawsfile "`project'/paperB/paperBresult/robustness/country_bootstrap_draw_assignments.csv"
if "`outroot'"=="" local outroot "`project'/paperB/paperBresult/robustness"
if "`reps'"=="" local reps 30
capture mkdir "`outroot'"
capture log close _all
log using "`outroot'/country_bootstrap.log", text replace name(bootlog)

local sourcefile "`project'/data0804/invest_panel_weo.csv"
local wsdifile "`project'/WSDI/data/processed/wsdi_sovereign61_1995_2018.csv"
foreach f in "`sourcefile'" "`wsdifile'" "`drawsfile'" {
    capture confirm file "`f'"
    if _rc {
        display as error "Required bootstrap input not found: `f'"
        log close bootlog
        exit 601
    }
}

* Build the shared, scaled source panel once. Lags and leads are deliberately
* created only after a sampled country block receives its new bootstrap ID.
tempfile wsdi base draws
import delimited using "`wsdifile'", clear varnames(1) case(preserve) encoding(UTF-8) asdouble
keep iso3 year wsdi_days
isid iso3 year
save `wsdi', replace

import delimited using "`sourcefile'", clear varnames(1) case(preserve) encoding(UTF-8)
isid iso3 year
merge 1:1 iso3 year using `wsdi', keep(master match) keepusing(wsdi_days) nogen
local ratio_vars bond_spreads bond_10y readiness100 growth inflation_cpi debt_gdp PrimaryBalance_gdp reserves tt Revenue_gdp OverallBalance_gdp interest_revenue
foreach v of local ratio_vars {
    recast double `v'
    replace `v' = `v'/100
}
recast double wsdi_days
replace wsdi_days = wsdi_days/100
keep country_name iso3 year bond_spreads readiness100 growth inflation_cpi debt_gdp reserves tt wsdi_days ConstantGDP
save `base', replace

import delimited using "`drawsfile'", clear varnames(1) case(preserve) encoding(UTF-8)
confirm variable replicate draw_slot source_iso3
keep if replicate<=`reps'
quietly summarize replicate, meanonly
assert r(min)==1 & r(max)==`reps'
isid replicate draw_slot
save `draws', replace

tempname p_boot
postfile `p_boot' str16 specification int replicate str12 status str24 failure_stage str48 failure_reason double cutoff beta_L beta_H rss N countries N_low N_high using "`outroot'/country_bootstrap_replications.dta", replace

forvalues rep=1/`reps' {
    display as text "OUTER BOOTSTRAP REPLICATION `rep'/`reps'"
    use `draws', clear
    keep if replicate==`rep'
    rename source_iso3 iso3
    joinby iso3 using `base'
    rename draw_slot boot_country_id
    isid boot_country_id year
    xtset boot_country_id year

    quietly tabulate year, generate(__year_fe_)
    ds __year_fe_*
    local year_dummies `r(varlist)'
    local base_year_dummy : word 1 of `year_dummies'
    local year_dummies : list year_dummies - base_year_dummy

    generate double spread_lag = L.bond_spreads
    generate double b_current = debt_gdp
    generate double b_lagged = L.debt_gdp
    generate double T_it = ConstantGDP/L.ConstantGDP if !missing(ConstantGDP,L.ConstantGDP) & L.ConstantGDP!=0
    generate double T_lead = F.T_it
    generate double b_outcome = F.debt_gdp-debt_gdp if !missing(F.debt_gdp,debt_gdp)

    * The T equation is identical in the two specifications, so estimate it once
    * per paired draw and reuse its coefficients without reusing any outcome fit.
    egen int tax_missing = rowmiss(T_lead T_it readiness100 wsdi_days inflation_cpi reserves tt)
    generate byte sample_tax = tax_missing==0
    quietly summarize readiness100 if sample_tax, meanonly
    scalar mean_A_T = r(mean)
    quietly summarize wsdi_days if sample_tax, meanonly
    scalar mean_X_T = r(mean)
    generate double c_A_T = readiness100-scalar(mean_A_T)
    generate double c_X_T = wsdi_days-scalar(mean_X_T)
    generate double int_AX_T = c_A_T*c_X_T
    capture quietly xtlsdvc T_lead c_A_T c_X_T int_AX_T inflation_cpi reserves tt `year_dummies', initial(bb) bias(2) vcov(0)
    local tax_rc = _rc
    if `tax_rc' {
        foreach spec in current lagged {
            post `p_boot' ("`spec'_debt") (`rep') ("failed") ("T_lsdvc") ("r(`tax_rc')") (.) (.) (.) (.) (.) (.) (.) (.)
        }
        continue
    }
    scalar gamma_A_centered = _b[c_A_T]
    scalar gamma_AX = _b[int_AX_T]
    scalar gamma_A_raw = scalar(gamma_A_centered)-scalar(gamma_AX)*scalar(mean_X_T)
    generate double TA_hat = scalar(gamma_A_raw)+scalar(gamma_AX)*wsdi_days if sample_tax

    foreach spec in current lagged {
        local state b_`spec'
        capture drop spread_missing sample_spread c_A c_X c_b int_AB int_AX mA_hat theta_hat_A debt_missing sample_debt __xL __xH
        egen int spread_missing = rowmiss(bond_spreads spread_lag readiness100 wsdi_days `state' growth inflation_cpi reserves tt)
        generate byte sample_spread = spread_missing==0
        quietly summarize readiness100 if sample_spread, meanonly
        scalar mean_A = r(mean)
        quietly summarize wsdi_days if sample_spread, meanonly
        scalar mean_X = r(mean)
        quietly summarize `state' if sample_spread, meanonly
        scalar mean_b = r(mean)
        generate double c_A = readiness100-scalar(mean_A)
        generate double c_X = wsdi_days-scalar(mean_X)
        generate double c_b = `state'-scalar(mean_b)
        generate double int_AB = c_A*c_b
        generate double int_AX = c_A*c_X
        capture quietly xtlsdvc bond_spreads c_A c_X c_b int_AB int_AX growth inflation_cpi reserves tt `year_dummies', initial(bb) bias(2) vcov(0)
        local spread_rc = _rc
        if `spread_rc' {
            post `p_boot' ("`spec'_debt") (`rep') ("failed") ("spread_lsdvc") ("r(`spread_rc')") (.) (.) (.) (.) (.) (.) (.) (.)
            continue
        }
        scalar beta_A_centered = _b[c_A]
        scalar beta_AB = _b[int_AB]
        scalar beta_AX = _b[int_AX]
        scalar beta_A_raw = scalar(beta_A_centered)-scalar(beta_AB)*scalar(mean_b)-scalar(beta_AX)*scalar(mean_X)
        generate double mA_hat = -(scalar(beta_A_raw)+scalar(beta_AB)*`state'+scalar(beta_AX)*wsdi_days) if sample_spread
        generate double theta_hat_A = `state'*mA_hat+TA_hat if sample_spread & sample_tax & !missing(`state',mA_hat,TA_hat)
        egen int debt_missing = rowmiss(b_outcome readiness100 theta_hat_A wsdi_days growth inflation_cpi reserves tt)
        generate byte sample_debt = debt_missing==0
        quietly count if sample_debt
        scalar N_debt = r(N)
        if scalar(N_debt)<100 {
            post `p_boot' ("`spec'_debt") (`rep') ("failed") ("debt_sample") ("N<100") (.) (.) (.) (.) (scalar(N_debt)) (.) (.) (.)
            continue
        }

        format theta_hat_A %24.17g
        quietly levelsof theta_hat_A if sample_debt, local(candidates) clean
        scalar best_rss = .
        scalar best_cutoff = .
        scalar best_low = .
        scalar best_high = .
        generate double __xL = .
        generate double __xH = .
        local candidate_total : word count `candidates'
        local candidate_index = 0
        foreach c of local candidates {
            local candidate_index = `candidate_index'+1
            quietly count if sample_debt & theta_hat_A<=`c'
            local nlow = r(N)
            quietly count if sample_debt & theta_hat_A>`c'
            local nhigh = r(N)
            if `candidate_index'>1 & `candidate_index'<`candidate_total' {
                quietly replace __xL = readiness100*max(`c'-theta_hat_A,0) if sample_debt
                quietly replace __xH = readiness100*max(theta_hat_A-`c',0) if sample_debt
                capture quietly areg b_outcome __xL __xH wsdi_days growth inflation_cpi reserves tt i.year if sample_debt, absorb(boot_country_id) vce(cluster boot_country_id)
                if !_rc {
                    local this_rss = e(rss)
                    if missing(scalar(best_rss)) | `this_rss'<scalar(best_rss) {
                        scalar best_rss = `this_rss'
                        scalar best_cutoff = `c'
                        scalar best_low = `nlow'
                        scalar best_high = `nhigh'
                    }
                }
            }
        }
        if missing(scalar(best_cutoff)) {
            post `p_boot' ("`spec'_debt") (`rep') ("failed") ("cutoff_search") ("no admissible fit") (.) (.) (.) (.) (scalar(N_debt)) (.) (.) (.)
            continue
        }
        quietly replace __xL = readiness100*max(scalar(best_cutoff)-theta_hat_A,0) if sample_debt
        quietly replace __xH = readiness100*max(theta_hat_A-scalar(best_cutoff),0) if sample_debt
        capture quietly areg b_outcome __xL __xH wsdi_days growth inflation_cpi reserves tt i.year if sample_debt, absorb(boot_country_id) vce(cluster boot_country_id)
        local debt_rc = _rc
        if `debt_rc' {
            post `p_boot' ("`spec'_debt") (`rep') ("failed") ("debt_final") ("r(`debt_rc')") (scalar(best_cutoff)) (.) (.) (.) (scalar(N_debt)) (.) (scalar(best_low)) (scalar(best_high))
            continue
        }
        assert scalar(best_low)+scalar(best_high)==e(N)
        post `p_boot' ("`spec'_debt") (`rep') ("success") ("") ("") (scalar(best_cutoff)) (_b[__xL]) (_b[__xH]) (e(rss)) (e(N)) (e(N_clust)) (scalar(best_low)) (scalar(best_high))
    }
}
postclose `p_boot'

use "`outroot'/country_bootstrap_replications.dta", clear
sort specification replicate
format cutoff beta_L beta_H rss %21.15g
export delimited using "`outroot'/country_bootstrap_replications.csv", replace datafmt
quietly count
assert r(N)==2*`reps'
display as result "COUNTRY BOOTSTRAP COMPLETE: requested paired replications=`reps'; retained rows=" r(N)
log close bootlog
