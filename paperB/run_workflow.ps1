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

foreach ($path in @($dataFile, $renderer) + $stages.Script) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required workflow input not found: $path"
    }
}

$inputHeader = (Get-Content -LiteralPath $dataFile -Encoding UTF8 -TotalCount 1).Split(',')
foreach ($field in @(
    'ConstantGDP', 'debt_gdp', 'growth',
    'vulnerability_delta100', 'readiness_delta100'
)) {
    if ($inputHeader -notcontains $field) {
        throw "Analysis input is missing required field: $field"
    }
}
$inputRows = @(Import-Csv -LiteralPath $dataFile)
foreach ($field in @('ConstantGDP')) {
    $nonpositive = @($inputRows | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_.$field) -and [double]$_.$field -le 0
    })
    if ($nonpositive.Count -gt 0) {
        throw "$field contains $($nonpositive.Count) nonpositive rows; its natural log is undefined."
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
    (Join-Path $ProjectRoot 'baseline\stata_outputs\model_stats.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.dta'),
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
    foreach ($line in Get-Content -LiteralPath $path -Encoding UTF8 | Where-Object { $_ -match '^\|' }) {
        $count = ([regex]::Matches($line, '(?<!\\)\|')).Count
        if ($count -lt 2) {
            throw "Malformed Markdown table row in $path`: $line"
        }
    }
}

$resultsText = Get-Content -Raw -LiteralPath $resultsFile -Encoding UTF8
foreach ($requiredText in @(
    '\ln(ConstantGDP)',
    'Y_{i,t+1}=\frac{ConstantGDP_{i,t+1}}{ConstantGDP_{it}}',
    'Y_{it}=\frac{ConstantGDP_{it}}{ConstantGDP_{i,t-1}}',
    '\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat Y^A_{it}',
    'b_{it}=debt\_gdp_{it}',
    '\Delta debt\_gdp_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}',
    'A_{it}-A_{i,t-1}',
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
        '$$A_{it}=\alpha_i',
        '\Delta b_{i,t+2}',
        '\rho_bb_{it}',
        '\rho_AA_{i,t-1}',
        '\ln(capitaGDP)',
        'Y_{it}=\ln(CurrentGDP_{it})',
        'ln_currentgdp'
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

$baselineCoefficientRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\model_coefficients.csv'))
$baselineModels = @('A_X_only','A_A_only','A_b_only','B_all_core','C_macro','Layer1_X','Layer2_A','Interact_AB','Interact_AX','Interact_all')
foreach ($model in $baselineModels) {
    foreach ($control in @('growth','ln_constantgdp')) {
        if (@($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq $control }).Count -ne 1) {
            throw "Baseline model $model must contain exactly one $control coefficient."
        }
    }
}
if (@($baselineCoefficientRows | Where-Object { $_.variable -eq 'debt_gdp' }).Count -eq 0 -or
    @($baselineCoefficientRows | Where-Object { $_.variable -eq 'ln_debt' }).Count -gt 0) {
    throw 'Baseline b mapping must use debt_gdp and not ln_debt.'
}
if (@($baselineCoefficientRows | Where-Object { $_.variable -eq 'ln_capitagdp' }).Count -gt 0) {
    throw 'Obsolete ln_capitagdp remains in baseline coefficient output.'
}
foreach ($field in @('vulnerability_delta100', 'readiness_delta100')) {
    if (@($baselineCoefficientRows | Where-Object { $_.variable -eq $field }).Count -eq 0) {
        throw "Baseline coefficient output is missing ND-GAIN delta regressor: $field"
    }
}
if (@($baselineCoefficientRows | Where-Object { $_.variable -in @('vulnerability100', 'readiness100') }).Count -gt 0) {
    throw 'An obsolete ND-GAIN level regressor remains in baseline coefficient output.'
}

$outputCoefficientRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'))
$outputModels = @('Spread_Interact_all','Y1_X_only','Y2_A_only','Y3_persistence','Y4_all_core','Y5_macro','Y6_layer1_X','Y7_layer2_A','Y8_interact_core','Y9_interact_macro','Y10_interact_full')
foreach ($control in @('growth','ln_constantgdp')) {
    if (@($outputCoefficientRows | Where-Object { $_.model -eq 'Spread_Interact_all' -and $_.variable -eq $control }).Count -ne 1) {
        throw "Empirical-theta spread model must contain exactly one $control coefficient."
    }
}
$persistentOutputModels = $outputModels | Where-Object { $_ -like 'Y*' }
foreach ($model in $persistentOutputModels) {
    if (@($outputCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'Y_lag' }).Count -ne 1 -or
        @($outputCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -in @('growth','ln_constantgdp') }).Count -ne 0) {
        throw "Empirical-theta model $model must use the output-ratio Y_lag and exclude growth/ln_constantgdp."
    }
}
if (@($outputCoefficientRows | Where-Object { $_.variable -eq 'ln_capitagdp' }).Count -gt 0) {
    throw 'Obsolete ln_capitagdp remains in empirical-theta coefficient output.'
}
if (@($outputCoefficientRows | Where-Object { $_.model -like 'T*' }).Count -gt 0 -or
    @($outputCoefficientRows | Where-Object { $_.model -like 'Y*' -and $_.variable -eq 'Y_lag' }).Count -ne 10) {
    throw 'Empirical-theta output must use Y models and Y_lag, not tax-base T models.'
}
foreach ($field in @('vulnerability_delta100', 'readiness_delta100')) {
    if (@($outputCoefficientRows | Where-Object { $_.variable -eq $field }).Count -eq 0) {
        throw "Empirical-theta coefficient output is missing ND-GAIN delta regressor: $field"
    }
}
if (@($outputCoefficientRows | Where-Object { $_.variable -in @('vulnerability100', 'readiness100') }).Count -gt 0) {
    throw 'An obsolete ND-GAIN level regressor remains in empirical-theta coefficient output.'
}
$thetaPanelRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.csv'))
$constantGdpByKey = @{}
foreach ($row in $thetaPanelRows) {
    $constantGdpByKey["$($row.iso3)|$([int]$row.year)"] = $row.ConstantGDP
}
$badOutputRatios = @($thetaPanelRows | Where-Object {
    $year = [int]$_.year
    $current = if ([string]::IsNullOrWhiteSpace($_.ConstantGDP)) { $null } else { [double]$_.ConstantGDP }
    $previousRaw = $constantGdpByKey["$($_.iso3)|$($year-1)"]
    $followingRaw = $constantGdpByKey["$($_.iso3)|$($year+1)"]
    $badLead = -not [string]::IsNullOrWhiteSpace($_.Y_outcome) -and (
        $null -eq $current -or [string]::IsNullOrWhiteSpace($followingRaw) -or
        [math]::Abs(([double]$_.Y_outcome) - ([double]$followingRaw / $current)) -gt 1e-9
    )
    $badLag = -not [string]::IsNullOrWhiteSpace($_.Y_lag) -and (
        $null -eq $current -or [string]::IsNullOrWhiteSpace($previousRaw) -or
        [math]::Abs(([double]$_.Y_lag) - ($current / [double]$previousRaw)) -gt 1e-9
    )
    $badB = -not [string]::IsNullOrWhiteSpace($_.b_it_theta) -and (
        [string]::IsNullOrWhiteSpace($_.debt_gdp) -or
        [math]::Abs(([double]$_.b_it_theta) - ([double]$_.debt_gdp)) -gt 1e-12
    )
    $badLead -or $badLag -or $badB
})
if ($thetaPanelRows.Count -eq 0 -or $badOutputRatios.Count -gt 0) {
    throw 'Empirical-theta panel fails the adjacent-year ConstantGDP ratio or debt_gdp mapping contract.'
}
$doomCoefficientRows = Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_coefficients.csv')
if (@($doomCoefficientRows | Where-Object { $_.variable -in @('debt_gdp', 'ln_debt', 'readiness_lag') }).Count -gt 0) {
    throw 'A retained Doomloop main specification contains a forbidden state control.'
}
if (@($doomCoefficientRows | Where-Object { $_.model -like 'RN*' -or $_.model -like 'D[123]_*' -or $_.model -like 'R[123]_*' }).Count -gt 0) {
    throw 'An obsolete state or readiness-own-cutoff model remains in the retained coefficient output.'
}
foreach ($model in @('DN1_core','DN2_macro','DN3_full','RDN1_core','RDN2_macro','RDN3_full')) {
    foreach ($control in @('growth','ln_constantgdp')) {
        if (@($doomCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq $control }).Count -ne 1) {
            throw "Doomloop model $model must contain exactly one $control coefficient."
        }
    }
}
if (@($doomCoefficientRows | Where-Object { $_.variable -eq 'ln_capitagdp' }).Count -gt 0) {
    throw 'Obsolete ln_capitagdp remains in Doomloop coefficient output.'
}
if (@($doomCoefficientRows | Where-Object { $_.variable -eq 'vulnerability_delta100' }).Count -eq 0 -or
    @($doomCoefficientRows | Where-Object { $_.variable -in @('vulnerability100', 'readiness100') }).Count -gt 0) {
    throw 'Doomloop coefficient output must use vulnerability_delta100 and no ND-GAIN level regressor.'
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
$readinessPanel = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop_nostate_panel.csv'))
$debtGdpByKey = @{}
foreach ($row in $readinessPanel) {
    $debtGdpByKey["$($row.iso3)|$([int]$row.year)"] = $row.debt_gdp
}
$badDebtChanges = @($readinessPanel | Where-Object {
    if ([string]::IsNullOrWhiteSpace($_.b_outcome)) { return $false }
    $followingRaw = $debtGdpByKey["$($_.iso3)|$([int]$_.year+1)"]
    [string]::IsNullOrWhiteSpace($_.debt_gdp) -or
    [string]::IsNullOrWhiteSpace($followingRaw) -or
    [math]::Abs(([double]$_.b_outcome) - (([double]$followingRaw) - ([double]$_.debt_gdp))) -gt 1e-9
})
$badReadinessChanges = @($readinessPanel | Where-Object {
    -not [string]::IsNullOrWhiteSpace($_.A_outcome) -and (
        [string]::IsNullOrWhiteSpace($_.readiness_lag) -or
        [math]::Abs(([double]$_.A_outcome) - (([double]$_.readiness_delta100) - ([double]$_.readiness_lag))) -gt 1e-9 -or
        [double]$_.A_outcome_year -ne [double]$_.year
    )
})
if ($readinessPanel.Count -eq 0 -or $badReadinessChanges.Count -gt 0) {
    throw 'Readiness outcome must equal current readiness minus its strict prior-year panel lag.'
}
if ($badDebtChanges.Count -gt 0) {
    throw 'Debt outcome must equal next-year debt_gdp minus current debt_gdp.'
}

$criterionRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\criterion_comparison.csv'))
$criterionNames = @('theta', 'b', 'mA', 'YA', 'b*mA')
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
