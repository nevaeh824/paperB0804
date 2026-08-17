[CmdletBinding()]
param(
    [string]$ProjectRoot = '',
    [string]$StataExe = 'C:\Environment_tools\Stata18\StataMP-64.exe',
    [switch]$SkipStata
)

$ErrorActionPreference = 'Stop'
$paperRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $paperRoot
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$projectRootStata = $ProjectRoot.Replace('\', '/')

$dataFile = Join-Path $ProjectRoot 'data0804\invest_panel_weo.csv'
$wsdiFile = Join-Path $ProjectRoot 'WSDI\data\processed\wsdi_sovereign61_1995_2018.csv'
$renderer = Join-Path $paperRoot 'render_output.py'
$codeRoot = Join-Path $paperRoot 'code'
$figureSource = Join-Path $ProjectRoot 'doomloop\figures'
$figureTarget = Join-Path $paperRoot 'figures'
$resultsFile = Join-Path $paperRoot 'paperB_results.md'
$diagnosticsFile = Join-Path $paperRoot 'paperB_diagnostics.md'
$progressFile = Join-Path $paperRoot 'progress.md'

$stages = @(
    [pscustomobject]@{
        Name = 'baseline'
        Script = Join-Path $codeRoot 'baseline_twfe.do'
        Log = Join-Path $ProjectRoot 'baseline\stata_outputs\baseline_twfe.log'
        Marker = 'ANALYSIS COMPLETE.'
    }
    [pscustomobject]@{
        Name = 'empirical_theta'
        Script = Join-Path $codeRoot 'empirical_theta.do'
        Log = Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta.log'
        Marker = 'ANALYSIS COMPLETE.'
    }
    [pscustomobject]@{
        Name = 'doomloop_no_state'
        Script = Join-Path $codeRoot 'doomloop_no_state.do'
        Log = Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop_no_state.log'
        Marker = 'ANALYSIS COMPLETE NO-STATE'
    }
)

foreach ($path in @($dataFile, $wsdiFile, $renderer) + $stages.Script) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required workflow input not found: $path"
    }
}

$totalSteps = $stages.Count + 3
if (-not $SkipStata) {
    if (-not (Test-Path -LiteralPath $StataExe -PathType Leaf)) {
        throw "Stata executable not found: $StataExe"
    }

    $stageNumber = 1
    foreach ($stage in $stages) {
        Write-Host "[$stageNumber/$totalSteps] Running $($stage.Name)..."
        $scriptStata = $stage.Script.Replace('\', '/')
        $stataArguments = @('/e', 'do', "`"$scriptStata`"", "`"$projectRootStata`"")
        $process = Start-Process -FilePath $StataExe `
            -ArgumentList $stataArguments `
            -WorkingDirectory $ProjectRoot -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            throw "Stata stage $($stage.Name) exited with code $($process.ExitCode)."
        }
        if (-not (Test-Path -LiteralPath $stage.Log -PathType Leaf)) {
            throw "Stata stage log not found: $($stage.Log)"
        }
        $logText = Get-Content -Raw -LiteralPath $stage.Log -Encoding UTF8
        if (-not $logText.Contains($stage.Marker)) {
            throw "Completion marker missing from $($stage.Log): $($stage.Marker)"
        }
        if ($logText -match '(?m)^r\([0-9]+\);\s*$') {
            throw "Stata runtime error found in $($stage.Log)."
        }
        $stageNumber++
    }
}
else {
    Write-Host '[Stata skipped] Validating existing machine-readable outputs...'
}

$requiredOutputs = @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'baseline\stata_outputs\model_coefficients.dta'),
    (Join-Path $ProjectRoot 'baseline\stata_outputs\model_stats.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\baseline_validation.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.dta'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_coefficients.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_stats.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_wald_tests.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoffs.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoff_validation.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_comparison.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_rss_profiles.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_cutoff_validation.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_marginal_curve_debt.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_marginal_curve_ready_debt_cutoff.csv')
)
foreach ($path in $requiredOutputs) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Required machine-readable output missing or empty: $path"
    }
}

# Fail closed unless every reported model and every row-level sample flag uses
# the exact same full-workflow country-year sample.
$allStatsRows = @(
    Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\model_stats.csv')
) + @(
    Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_stats.csv')
) + @(
    Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_stats.csv')
)
$regressionSampleSizes = @($allStatsRows | ForEach-Object { [int][double]$_.N } | Sort-Object -Unique)
if ($regressionSampleSizes.Count -ne 1) {
    throw "Cross-stage regression sample drift detected: $($regressionSampleSizes -join ', ')."
}

$baselineAudit = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\sample_audit.csv'))
$thetaPanel = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.csv'))
$doomPanel = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop_nostate_panel.csv'))
foreach ($field in @('sample_common_all', 'sample_spread', 'sample_tax', 'sample_theta_support', 'theta_constructible')) {
    if (-not ($thetaPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Empirical-theta panel is missing the full-workflow sample flag: $field"
    }
}
foreach ($field in @('sample_common_all', 'sample_debt_ns', 'sample_ready_ns')) {
    if (-not ($doomPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Doomloop panel is missing the full-workflow sample flag: $field"
    }
}

$commonKeys = @($thetaPanel | Where-Object { $_.sample_common_all -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
$sampleKeyGroups = @{
    baseline = @($baselineAudit | Where-Object { $_.sample_common_all -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
    spread = @($thetaPanel | Where-Object { $_.sample_spread -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
    tax = @($thetaPanel | Where-Object { $_.sample_tax -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
    theta = @($thetaPanel | Where-Object { $_.sample_theta_support -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
    debt = @($doomPanel | Where-Object { $_.sample_debt_ns -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
    readiness = @($doomPanel | Where-Object { $_.sample_ready_ns -eq '1' } | ForEach-Object { "$($_.iso3)|$($_.year)" } | Sort-Object -Unique)
}
foreach ($keys in $sampleKeyGroups.Values) {
    if (@(Compare-Object -ReferenceObject $commonKeys -DifferenceObject $keys).Count -ne 0) {
        throw 'Country-year keys drift across full-workflow sample flags.'
    }
}
if ($commonKeys.Count -ne $regressionSampleSizes[0]) {
    throw 'The full-workflow common key count differs from reported regression N.'
}
foreach ($row in $thetaPanel) {
    $inCommon = $row.sample_common_all -eq '1'
    if (($row.sample_spread -eq '1') -ne $inCommon -or ($row.sample_tax -eq '1') -ne $inCommon -or ($row.sample_theta_support -eq '1') -ne $inCommon -or ($row.theta_constructible -eq '1') -ne $inCommon) {
        throw "Empirical-theta sample aliases drift at $($row.iso3) $($row.year)."
    }
    foreach ($field in @('mA_hat', 'TA_hat', 'theta_hat_A')) {
        $present = -not [string]::IsNullOrWhiteSpace($row.$field) -and $row.$field -ne '.'
        if ($present -ne $inCommon) {
            throw "$field availability does not match the full-workflow sample at $($row.iso3) $($row.year)."
        }
    }
}

$copyStep = $stages.Count + 1
Write-Host "[$copyStep/$totalSteps] Copying current main-specification figure assets..."
if (-not (Test-Path -LiteralPath $figureSource -PathType Container)) {
    throw "Figure source directory not found: $figureSource"
}
New-Item -ItemType Directory -Force -Path $figureTarget | Out-Null
$requiredFigures = @(
    'debt_marginal_effect_no_b.png',
    'debt_marginal_effect_no_b.pdf',
    'readiness_marginal_effect_debt_cutoff_no_lag.png',
    'readiness_marginal_effect_debt_cutoff_no_lag.pdf',
    'kink_marginal_effects_no_state.png',
    'kink_marginal_effects_no_state.pdf'
)
foreach ($name in $requiredFigures) {
    $source = Join-Path $figureSource $name
    if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or (Get-Item -LiteralPath $source).Length -eq 0) {
        throw "Required source figure missing or empty: $source"
    }
    Copy-Item -LiteralPath $source -Destination (Join-Path $figureTarget $name) -Force
}

# Remove only known obsolete generated snapshots from the final paperB handoff.
$obsoleteFigures = @(
    'debt_marginal_effect.png', 'debt_marginal_effect.pdf',
    'readiness_marginal_effect.png', 'readiness_marginal_effect.pdf',
    'readiness_marginal_effect_debt_cutoff.png', 'readiness_marginal_effect_debt_cutoff.pdf',
    'readiness_marginal_effect_no_lag.png', 'readiness_marginal_effect_no_lag.pdf',
    'kink_marginal_effects.png', 'kink_marginal_effects.pdf',
    'debt_marginal_effect_forward.png', 'debt_marginal_effect_forward.pdf',
    'debt_marginal_effect_no_b_forward.png', 'debt_marginal_effect_no_b_forward.pdf',
    'readiness_marginal_effect_forward.png', 'readiness_marginal_effect_forward.pdf',
    'readiness_marginal_effect_debt_cutoff_forward.png', 'readiness_marginal_effect_debt_cutoff_forward.pdf',
    'readiness_marginal_effect_no_lag_forward.png', 'readiness_marginal_effect_no_lag_forward.pdf',
    'readiness_marginal_effect_debt_cutoff_no_lag_forward.png', 'readiness_marginal_effect_debt_cutoff_no_lag_forward.pdf',
    'kink_marginal_effects_forward.png', 'kink_marginal_effects_forward.pdf',
    'kink_marginal_effects_no_state_forward.png', 'kink_marginal_effects_no_state_forward.pdf'
)
foreach ($name in $obsoleteFigures) {
    $path = Join-Path $figureTarget $name
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Remove-Item -LiteralPath $path -Force
    }
}

$renderStep = $stages.Count + 2
Write-Host "[$renderStep/$totalSteps] Rendering results, diagnostics, and progress documents..."
$python = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $python) {
    & $python.Source -3.14 $renderer
}
else {
    $python = Get-Command python -ErrorAction Stop
    & $python.Source $renderer
}
if ($LASTEXITCODE -ne 0) {
    throw "Integrated renderer failed with code $LASTEXITCODE"
}

$qaStep = $stages.Count + 3
Write-Host "[$qaStep/$totalSteps] Running integrated QA..."
foreach ($path in @($resultsFile, $diagnosticsFile, $progressFile)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Integrated document was not generated: $path"
    }
    $text = Get-Content -Raw -LiteralPath $path -Encoding UTF8
    if ($text -match 'PaperB_DoomLoop_') {
        throw "Forbidden draft reference found in $path"
    }
    if ($text.Contains('ln_currentgdp') -or $text.Contains('\ln(CurrentGDP')) {
        throw "Obsolete CurrentGDP Baseline-control text found in $path"
    }
    if ($text.Contains('vulnerability') -or $text.Contains('脆弱性')) {
        throw "Obsolete vulnerability-based X text found in $path"
    }
    if ($text.Contains('taxgdp') -or $text.Contains('taxbase_lag')) {
        throw "Obsolete taxgdp-based T text found in $path"
    }
    foreach ($line in Get-Content -LiteralPath $path -Encoding UTF8 | Where-Object { $_ -match '^\|' }) {
        $count = ([regex]::Matches($line, '(?<!\\)\|')).Count
        if ($count -lt 2) {
            throw "Malformed Markdown table row in $path`: $line"
        }
    }
}

$resultsText = Get-Content -Raw -LiteralPath $resultsFile -Encoding UTF8
foreach ($requiredText in @(
    'T_{it}=\frac{\ln(ConstantGDP_{it})}{\ln(ConstantGDP_{i,t-1})}',
    'T_{i,t+1}=\frac{\ln(ConstantGDP_{i,t+1})}{\ln(ConstantGDP_{it})}=F.T_{it}',
    'X_{it}=wsdi\_days_{it}\times0.01',
    '\rho_s s_{i,t-1}',
    'b^{pre}_{it}=b_{i,t-1}=debt\_gdp_{i,t-1}',
    '不控制 $\ln(ConstantGDP)$',
    'T 指标方程的宏观控制仅为 Inflation，不控制 Growth',
    '\widehat\theta^A_{it}=b^{pre}_{it}\widehat m^A_{it}+\widehat T^A_{it}',
    '\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}',
    '\beta_LA_{it}(c-\widehat\theta^A_{it})_+',
    '\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+',
    'Criterion Decomposition / Competing Criterion Test',
    '| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N_low | N_high |'
)) {
    if (-not $resultsText.Contains($requiredText)) {
        throw "Required formula or table text missing from integrated results: $requiredText"
    }
}

foreach ($path in @($resultsFile, $diagnosticsFile, $progressFile)) {
    $text = Get-Content -Raw -LiteralPath $path -Encoding UTF8
    foreach ($forbiddenText in @(
        'doomloop_forward',
        'doomloop-h2',
        '两期前瞻',
        '\Delta b_{i,t+2}',
        '\rho_bb_{it}',
        '\rho_AA_{i,t-1}'
    )) {
        if ($text.Contains($forbiddenText)) {
            throw "Obsolete specification text found in $path`: $forbiddenText"
        }
    }
}

$validationFiles = @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoff_validation.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_cutoff_validation.csv')
)
foreach ($path in $validationFiles) {
    $failed = @(Import-Csv -LiteralPath $path | Where-Object { $_.passed -ne '1' })
    if ($failed.Count -gt 0) {
        throw "Validation failure recorded in $path"
    }
}

foreach ($path in @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\unit_scaling_checks.csv')
)) {
    $wsdiRows = @(Import-Csv -LiteralPath $path | Where-Object { $_.variable -eq 'wsdi_days' })
    if ($wsdiRows.Count -ne 1 -or $wsdiRows[0].passed -ne '1' -or [math]::Abs([double]$wsdiRows[0].max_abs_scaling_diff) -gt 1e-12) {
        throw "WSDI scaling audit must contain one passing wsdi_days * 0.01 row: $path"
    }
}

$forbiddenGdpControls = @('CurrentGDP', 'ConstantGDP', 'ln_currentgdp', 'ln_constantgdp')
$allBaselineModels = @('A_X_only', 'A_A_only', 'A_b_only', 'B_all_core', 'C_macro', 'Layer1_X', 'Layer2_A', 'Interact_AB', 'Interact_AX', 'Interact_all')
$baselineCoefficientRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\model_coefficients.csv'))
foreach ($model in $allBaselineModels) {
    $lagRows = @($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'spread_lag' })
    if ($lagRows.Count -ne 1 -or $lagRows[0].omitted -ne '0' -or [string]::IsNullOrWhiteSpace($lagRows[0].coefficient) -or $lagRows[0].coefficient -eq '.' -or [string]::IsNullOrWhiteSpace($lagRows[0].se) -or $lagRows[0].se -eq '.') {
        throw "Baseline model $model must contain exactly one non-omitted, numeric spread_lag control."
    }
    $lagCoefficient = [double]$lagRows[0].coefficient
    $lagSe = [double]$lagRows[0].se
    if ([double]::IsNaN($lagCoefficient) -or [double]::IsInfinity($lagCoefficient) -or [double]::IsNaN($lagSe) -or [double]::IsInfinity($lagSe) -or $lagSe -le 0) {
        throw "Baseline model $model has an invalid spread_lag coefficient or standard error."
    }
}
$baselineRawXModels = @('A_X_only', 'B_all_core', 'C_macro', 'Layer1_X', 'Layer2_A')
foreach ($model in $baselineRawXModels) {
    if (@($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'wsdi_days' }).Count -ne 1) {
        throw "Baseline model $model must use wsdi_days as X."
    }
}
if (@($baselineCoefficientRows | Where-Object { $_.variable -eq 'vulnerability100' }).Count -gt 0) {
    throw 'A Baseline model still uses vulnerability100 as X.'
}
$baselineRawBModels = @('A_b_only', 'B_all_core', 'C_macro', 'Layer1_X', 'Layer2_A')
foreach ($model in $baselineRawBModels) {
    if (@($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'b_pre' }).Count -ne 1 -or @($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'debt_gdp' }).Count -gt 0) {
        throw "Baseline model $model must use b_pre rather than contemporaneous debt_gdp."
    }
}
$baselineGdpRows = @($baselineCoefficientRows | Where-Object { $_.variable -in $forbiddenGdpControls })
if ($baselineGdpRows.Count -gt 0) {
    throw 'A Baseline model still contains a forbidden GDP control.'
}

$taxCoefficientRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'))
$spreadCoefficientRows = @($taxCoefficientRows | Where-Object { $_.model -eq 'Spread_Interact_all' })
$spreadLagRows = @($spreadCoefficientRows | Where-Object { $_.variable -eq 'spread_lag' })
if ($spreadLagRows.Count -ne 1 -or $spreadLagRows[0].omitted -ne '0' -or [string]::IsNullOrWhiteSpace($spreadLagRows[0].coefficient) -or $spreadLagRows[0].coefficient -eq '.' -or [string]::IsNullOrWhiteSpace($spreadLagRows[0].se) -or $spreadLagRows[0].se -eq '.') {
    throw 'Empirical-theta spread validation must contain exactly one non-omitted, numeric spread_lag control.'
}
$spreadLagCoefficient = [double]$spreadLagRows[0].coefficient
$spreadLagSe = [double]$spreadLagRows[0].se
if ([double]::IsNaN($spreadLagCoefficient) -or [double]::IsInfinity($spreadLagCoefficient) -or [double]::IsNaN($spreadLagSe) -or [double]::IsInfinity($spreadLagSe) -or $spreadLagSe -le 0) {
    throw 'Empirical-theta spread_lag coefficient or standard error is invalid.'
}
$spreadGdpRows = @($spreadCoefficientRows | Where-Object { $_.variable -in $forbiddenGdpControls })
if ($spreadGdpRows.Count -gt 0) {
    throw 'Empirical-theta spread validation still contains a GDP control.'
}
if (@($taxCoefficientRows | Where-Object { $_.model -like 'T*' -and $_.variable -in $forbiddenGdpControls }).Count -gt 0) {
    throw 'T-indicator equation contains a forbidden separate GDP control.'
}
$taxRawXModels = @('T1_X_only', 'T4_all_core', 'T5_macro', 'T6_layer1_X', 'T7_layer2_A')
foreach ($model in $taxRawXModels) {
    if (@($taxCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'wsdi_days' }).Count -ne 1) {
        throw "Tax-base model $model must use wsdi_days as X."
    }
}
if (@($taxCoefficientRows | Where-Object { $_.variable -eq 'vulnerability100' }).Count -gt 0) {
    throw 'An empirical-theta model still uses vulnerability100 as X.'
}
$tPersistenceModels = @('T3_persistence', 'T4_all_core', 'T5_macro', 'T6_layer1_X', 'T7_layer2_A', 'T8_interact_core', 'T9_interact_macro', 'T10_interact_full')
foreach ($model in $tPersistenceModels) {
    if (@($taxCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'T_it' }).Count -ne 1) {
        throw "T-indicator model $model must control the new T_it measure."
    }
}
if (@($taxCoefficientRows | Where-Object { $_.variable -in @('taxgdp', 'taxbase_lag') }).Count -gt 0) {
    throw 'An empirical-theta model still uses a taxgdp-based T measure.'
}
if (@($taxCoefficientRows | Where-Object { $_.model -like 'T*' -and $_.variable -eq 'growth' }).Count -gt 0) {
    throw 'A retained T-indicator model still controls for growth.'
}
$baselineValidationRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\baseline_validation.csv'))
$expectedBaselineValidationVariables = @('c_A', 'c_X', 'c_b', 'int_AB', 'int_AX', 'spread_lag', 'growth', 'inflation_cpi', 'reserves', 'tt')
if ($baselineValidationRows.Count -ne $expectedBaselineValidationVariables.Count) {
    throw 'Empirical-theta Baseline validation has an unexpected row count.'
}
foreach ($variable in $expectedBaselineValidationVariables) {
    $rows = @($baselineValidationRows | Where-Object { $_.variable -eq $variable })
    if ($rows.Count -ne 1 -or [double]$rows[0].abs_b_diff -gt 1e-10 -or [double]$rows[0].abs_se_diff -gt 1e-8) {
        throw "Empirical-theta Baseline reproduction exceeds tolerance for $variable."
    }
}
$doomCoefficientRows = Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_coefficients.csv')
if (@($doomCoefficientRows | Where-Object { $_.variable -in ($forbiddenGdpControls + @('debt_gdp', 'readiness_lag')) }).Count -gt 0) {
    throw 'A retained Doomloop main specification contains a forbidden GDP or state control.'
}
if (@($doomCoefficientRows | Where-Object { $_.model -like 'RN*' -or $_.model -like 'D[123]_*' -or $_.model -like 'R[123]_*' }).Count -gt 0) {
    throw 'An obsolete state or readiness-own-cutoff model remains in the retained coefficient output.'
}
$doomModels = @($doomCoefficientRows.model | Sort-Object -Unique)
foreach ($model in $doomModels) {
    if (@($doomCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'wsdi_days' }).Count -ne 1) {
        throw "Retained Doomloop model $model must use wsdi_days as X."
    }
}
if (@($doomCoefficientRows | Where-Object { $_.variable -eq 'vulnerability100' }).Count -gt 0) {
    throw 'A retained Doomloop model still uses vulnerability100 as X.'
}

$baselineMetadataRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\run_metadata.csv') | Where-Object { $_.item -eq 'nonpositive_ConstantGDP' })
if ($baselineMetadataRows.Count -ne 1 -or [double]$baselineMetadataRows[0].value -ne 0) {
    throw 'Baseline metadata must report exactly zero nonpositive ConstantGDP rows.'
}
$thetaMetadataRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\run_metadata.csv') | Where-Object { $_.item -eq 'nonpositive_ConstantGDP_rows' })
if ($thetaMetadataRows.Count -ne 1 -or [double]$thetaMetadataRows[0].value -ne 0) {
    throw 'Empirical-theta metadata must report exactly zero nonpositive ConstantGDP rows.'
}

$statsRows = Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_stats.csv')
$cutoffRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoffs.csv'))
if ($cutoffRows.Count -ne 1 -or $cutoffRows[0].equation -ne 'debt') {
    throw 'nostate_cutoffs.csv must contain only the searched debt equation.'
}
$debtCutoff = [double]$cutoffRows[0].rss_min_cutoff
$readinessStats = @($statsRows | Where-Object { $_.model -like 'RDN*' })
if ($readinessStats.Count -ne 3) {
    throw 'Expected exactly three readiness models using the debt cutoff.'
}
foreach ($row in $readinessStats) {
    if ([math]::Abs(([double]$row.cutoff) - $debtCutoff) -gt 1e-10) {
        throw "Readiness model $($row.model) does not use the debt full-control cutoff."
    }
}

$criterionRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_comparison.csv'))
$criterionNames = @('theta', 'b_pre', 'mA', 'TA', 'b_pre*mA')
if ($criterionRows.Count -ne 5 -or (@($criterionRows.criterion | Sort-Object -Unique).Count -ne 5)) {
    throw 'Criterion comparison must contain exactly five unique criteria.'
}
foreach ($name in $criterionNames) {
    if (@($criterionRows | Where-Object { $_.criterion -eq $name }).Count -ne 1) {
        throw "Criterion comparison is missing or duplicates: $name"
    }
}
$commonN = [double]$criterionRows[0].N
foreach ($row in $criterionRows) {
    foreach ($field in @('cutoff','beta_L','p_L','beta_H','p_H','rss','r2_within','N','N_low','N_high')) {
        if ([string]::IsNullOrWhiteSpace($row.$field) -or $row.$field -eq '.') {
            throw "Criterion $($row.criterion) has a missing $field."
        }
    }
    $pL = [double]$row.p_L
    $pH = [double]$row.p_H
    if ($pL -lt 0 -or $pL -gt 1 -or $pH -lt 0 -or $pH -gt 1) {
        throw "Criterion $($row.criterion) has an invalid p-value."
    }
    if ([double]$row.rss -lt 0 -or [double]$row.N -ne $commonN) {
        throw "Criterion $($row.criterion) has invalid RSS or a drifting sample."
    }
    if ([double]$row.N_low + [double]$row.N_high -ne [double]$row.N) {
        throw "Criterion $($row.criterion) fails N_low + N_high = N."
    }
    $matchesTheory = ([double]$row.beta_L -gt 0 -and [double]$row.beta_H -lt 0)
    if ($matchesTheory -and -not $row.theoretical_signs.StartsWith('Match')) {
        throw "Criterion $($row.criterion) theoretical-sign label is inconsistent."
    }
    if (-not $matchesTheory -and $row.theoretical_signs.StartsWith('Match')) {
        throw "Criterion $($row.criterion) theoretical-sign label is inconsistent."
    }
}

$profileRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_rss_profiles.csv'))
foreach ($row in $criterionRows) {
    $profile = @($profileRows | Where-Object { $_.criterion -eq $row.criterion })
    if ($profile.Count -eq 0) {
        throw "No RSS profile found for criterion $($row.criterion)."
    }
    $minRss = ($profile | ForEach-Object { [double]$_.rss } | Measure-Object -Minimum).Minimum
    $chosen = @($profile | Where-Object { [math]::Abs(([double]$_.cutoff) - ([double]$row.cutoff)) -lt 1e-10 })
    if ($chosen.Count -ne 1 -or [math]::Abs(([double]$chosen[0].rss) - $minRss) -gt 1e-8) {
        throw "Recorded cutoff is not the unique RSS minimum row for criterion $($row.criterion)."
    }
}

$thetaRow = $criterionRows | Where-Object { $_.criterion -eq 'theta' }
$dn3Stats = $statsRows | Where-Object { $_.model -eq 'DN3_full' }
$dn3Low = $doomCoefficientRows | Where-Object { $_.model -eq 'DN3_full' -and $_.variable -eq 'debt_kink_low' }
$dn3High = $doomCoefficientRows | Where-Object { $_.model -eq 'DN3_full' -and $_.variable -eq 'debt_kink_high' }
foreach ($pair in @(
    @([double]$thetaRow.cutoff, [double]$dn3Stats.cutoff, 1e-10, 'cutoff'),
    @([double]$thetaRow.beta_L, [double]$dn3Low.coefficient, 1e-7, 'beta_L'),
    @([double]$thetaRow.p_L, [double]$dn3Low.p, 1e-7, 'p_L'),
    @([double]$thetaRow.beta_H, [double]$dn3High.coefficient, 1e-7, 'beta_H'),
    @([double]$thetaRow.p_H, [double]$dn3High.p, 1e-7, 'p_H'),
    @([double]$thetaRow.r2_within, [double]$dn3Stats.r2_within, 1e-7, 'within R2'),
    @([double]$thetaRow.N, [double]$dn3Stats.N, 0, 'N')
)) {
    if ([math]::Abs($pair[0] - $pair[1]) -gt $pair[2]) {
        throw "Theta criterion and DN3_full disagree on $($pair[3])."
    }
}

$readyCurve = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_marginal_curve_ready_debt_cutoff.csv'))
if (@($readyCurve | Where-Object { [math]::Abs(([double]$_.cutoff) - $debtCutoff) -gt 1e-10 }).Count -gt 0) {
    throw 'Readiness marginal curve does not consistently use the debt cutoff.'
}
$zeroNodes = @($readyCurve | Where-Object { [math]::Abs(([double]$_.theta) - $debtCutoff) -lt 1e-10 -and [math]::Abs(([double]$_.marginal_effect)) -lt 1e-12 })
if ($zeroNodes.Count -lt 1) {
    throw 'Readiness marginal curve lacks the zero-effect cutoff node.'
}

foreach ($name in $requiredFigures) {
    $path = Join-Path $figureTarget $name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Required final figure missing or empty: $path"
    }
}

Write-Host 'Paper B workflow complete.'
Write-Host "Results: $resultsFile"
Write-Host "Diagnostics: $diagnosticsFile"
Write-Host "Progress: $progressFile"
Write-Host "Workflow: $(Join-Path $paperRoot 'WORKFLOW.md')"
