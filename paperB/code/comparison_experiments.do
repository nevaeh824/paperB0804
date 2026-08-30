version 18.0
clear all
set more off
set varabbrev off
set linesize 255

* Cross-specification cutoff and common-sample comparisons. The two inputs are
* independently generated pipeline results; this script never rewrites them.
args project currentroot lagroot outroot
if "`project'"=="" local project "C:/Users/chenyu/Desktop/0805"
if "`currentroot'"=="" local currentroot "`project'/paperB/paperBresult"
if "`lagroot'"=="" local lagroot "`project'/paperB_debt_lag/paperB_debt_lag"
if "`outroot'"=="" local outroot "`currentroot'/robustness"
capture mkdir "`outroot'"
capture log close _all
log using "`outroot'/comparison_experiments.log", text replace name(comparelog)

local currentpanel "`currentroot'/doomloop/stata_outputs/doomloop_nostate_panel.csv"
local lagpanel "`lagroot'/doomloop/stata_outputs/doomloop_nostate_panel.csv"
local currentcut "`currentroot'/doomloop/stata_outputs/nostate_cutoffs.csv"
local lagcut "`lagroot'/doomloop/stata_outputs/nostate_cutoffs.csv"
foreach f in "`currentpanel'" "`lagpanel'" "`currentcut'" "`lagcut'" {
    capture confirm file "`f'"
    if _rc {
        display as error "Required comparison input not found: `f'"
        log close comparelog
        exit 601
    }
}

import delimited using "`currentcut'", clear varnames(1) case(preserve) encoding(UTF-8)
assert _N==1
quietly summarize rss_min_cutoff, meanonly
scalar cutoff_current = r(mean)
import delimited using "`lagcut'", clear varnames(1) case(preserve) encoding(UTF-8)
assert _N==1
quietly summarize rss_min_cutoff, meanonly
scalar cutoff_lagged = r(mean)

tempfile current
import delimited using "`currentpanel'", clear varnames(1) case(preserve) encoding(UTF-8)
keep country_name iso3 country_id year b_outcome readiness100 wsdi_days growth inflation_cpi reserves tt theta_hat_A sample_debt_ns
rename theta_hat_A theta_current
rename sample_debt_ns sample_current
isid iso3 year
save `current', replace

import delimited using "`lagpanel'", clear varnames(1) case(preserve) encoding(UTF-8)
keep iso3 year theta_hat_A sample_debt_ns
rename theta_hat_A theta_lagged
rename sample_debt_ns sample_lagged
isid iso3 year
merge 1:1 iso3 year using `current', assert(match) nogen
isid iso3 year
egen long panel_id = group(iso3), label
xtset panel_id year
local controls wsdi_days growth inflation_cpi reserves tt

* -----------------------------------------------------------------------------
* Fixed old/new cutoff cross sensitivity on each theta specification's natural
* full debt-equation sample.
* -----------------------------------------------------------------------------
tempname p_cross
postfile `p_cross' str16 theta_specification str16 cutoff_source double cutoff beta_L se_L p_L beta_H se_H p_H rss r2_within N countries N_low N_high using "`outroot'/cross_cutoff_sensitivity.dta", replace
foreach spec in current lagged {
    local qvar theta_`spec'
    local svar sample_`spec'
    foreach source in current lagged {
        local c = scalar(cutoff_`source')
        capture drop __xL __xH __est
        generate double __xL = readiness100*max(`c'-`qvar',0) if `svar'
        generate double __xH = readiness100*max(`qvar'-`c',0) if `svar'
        quietly xtreg b_outcome __xL __xH `controls' i.year if `svar', fe vce(cluster panel_id)
        scalar __r2w = e(r2_w)
        quietly areg b_outcome __xL __xH `controls' i.year if `svar', absorb(panel_id) vce(cluster panel_id)
        generate byte __est = e(sample)
        scalar __bL = _b[__xL]
        scalar __sL = _se[__xL]
        scalar __pL = 2*ttail(e(df_r),abs(_b[__xL]/_se[__xL]))
        scalar __bH = _b[__xH]
        scalar __sH = _se[__xH]
        scalar __pH = 2*ttail(e(df_r),abs(_b[__xH]/_se[__xH]))
        scalar __rss = e(rss)
        scalar __N = e(N)
        scalar __G = e(N_clust)
        quietly count if __est & `qvar'<=`c'
        scalar __NL = r(N)
        quietly count if __est & `qvar'>`c'
        scalar __NH = r(N)
        assert scalar(__NL)+scalar(__NH)==scalar(__N)
        post `p_cross' ("`spec'_debt") ("`source'_debt") (`c') (scalar(__bL)) (scalar(__sL)) (scalar(__pL)) (scalar(__bH)) (scalar(__sH)) (scalar(__pH)) (scalar(__rss)) (scalar(__r2w)) (scalar(__N)) (scalar(__G)) (scalar(__NL)) (scalar(__NH))
    }
}
postclose `p_cross'
preserve
    use "`outroot'/cross_cutoff_sensitivity.dta", clear
    format cutoff beta_L se_L p_L beta_H se_H p_H rss r2_within %21.15g
    export delimited using "`outroot'/cross_cutoff_sensitivity.csv", replace datafmt
restore

* -----------------------------------------------------------------------------
* Re-search each cutoff on the exact intersection of the two natural samples.
* -----------------------------------------------------------------------------
generate byte sample_common = sample_current==1 & sample_lagged==1
quietly count if sample_common
assert r(N)==742
preserve
    keep if sample_common
    keep iso3 year country_name country_id
    sort iso3 year
    isid iso3 year
    export delimited using "`outroot'/common_742_keys.csv", replace
restore

tempname p_common p_common_profile
postfile `p_common' str16 specification double cutoff beta_L se_L p_L beta_H se_H p_H rss r2_within N countries N_low N_high candidate_count trim_low trim_high using "`outroot'/common_742_specification.dta", replace
postfile `p_common_profile' str16 specification double cutoff rss N N_low N_high using "`outroot'/common_742_rss_profile.dta", replace

foreach spec in current lagged {
    local qvar theta_`spec'
    quietly summarize `qvar' if sample_common, detail
    scalar __trim_low = r(p10)
    scalar __trim_high = r(p90)
    format `qvar' %21.15g
    quietly levelsof `qvar' if sample_common & `qvar'>=scalar(__trim_low) & `qvar'<=scalar(__trim_high), local(candidates) clean
    scalar __best_rss = .
    scalar __best_cutoff = .
    scalar __best_low = .
    scalar __best_high = .
    scalar __candidate_count = 0
    local minside = max(50,ceil(.10*742))
    capture drop __xL __xH
    generate double __xL = .
    generate double __xH = .
    foreach c of local candidates {
        quietly count if sample_common & `qvar'<=`c'
        local nlow = r(N)
        quietly count if sample_common & `qvar'>`c'
        local nhigh = r(N)
        if `nlow'>=`minside' & `nhigh'>=`minside' {
            quietly replace __xL = readiness100*max(`c'-`qvar',0) if sample_common
            quietly replace __xH = readiness100*max(`qvar'-`c',0) if sample_common
            quietly areg b_outcome __xL __xH `controls' i.year if sample_common, absorb(panel_id) vce(cluster panel_id)
            local this_rss = e(rss)
            post `p_common_profile' ("`spec'_debt") (`c') (`this_rss') (e(N)) (`nlow') (`nhigh')
            scalar __candidate_count = scalar(__candidate_count)+1
            if missing(scalar(__best_rss)) | `this_rss'<scalar(__best_rss) {
                scalar __best_rss = `this_rss'
                scalar __best_cutoff = `c'
                scalar __best_low = `nlow'
                scalar __best_high = `nhigh'
            }
        }
    }
    assert !missing(scalar(__best_cutoff))
    quietly replace __xL = readiness100*max(scalar(__best_cutoff)-`qvar',0) if sample_common
    quietly replace __xH = readiness100*max(`qvar'-scalar(__best_cutoff),0) if sample_common
    quietly xtreg b_outcome __xL __xH `controls' i.year if sample_common, fe vce(cluster panel_id)
    scalar __r2w = e(r2_w)
    quietly areg b_outcome __xL __xH `controls' i.year if sample_common, absorb(panel_id) vce(cluster panel_id)
    scalar __bL = _b[__xL]
    scalar __sL = _se[__xL]
    scalar __pL = 2*ttail(e(df_r),abs(_b[__xL]/_se[__xL]))
    scalar __bH = _b[__xH]
    scalar __sH = _se[__xH]
    scalar __pH = 2*ttail(e(df_r),abs(_b[__xH]/_se[__xH]))
    assert e(N)==742
    assert scalar(__best_low)+scalar(__best_high)==e(N)
    post `p_common' ("`spec'_debt") (scalar(__best_cutoff)) (scalar(__bL)) (scalar(__sL)) (scalar(__pL)) (scalar(__bH)) (scalar(__sH)) (scalar(__pH)) (e(rss)) (scalar(__r2w)) (e(N)) (e(N_clust)) (scalar(__best_low)) (scalar(__best_high)) (scalar(__candidate_count)) (scalar(__trim_low)) (scalar(__trim_high))
    drop __xL __xH
}
postclose `p_common'
postclose `p_common_profile'

foreach name in common_742_specification common_742_rss_profile {
    preserve
        use "`outroot'/`name'.dta", clear
        capture format cutoff beta_L se_L p_L beta_H se_H p_H rss r2_within trim_low trim_high %21.15g
        capture format cutoff rss %21.15g
        export delimited using "`outroot'/`name'.csv", replace datafmt
    restore
}

display as result "COMPARISON EXPERIMENTS COMPLETE"
display as result "Current cutoff=" scalar(cutoff_current) "; lagged cutoff=" scalar(cutoff_lagged) "; common N=742"
log close comparelog
