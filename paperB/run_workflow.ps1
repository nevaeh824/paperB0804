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
$capacityFile = Join-Path $ProjectRoot 'data0804\ndgain_countryindex_2026\resources\vulnerability\capacity.csv'
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

foreach ($path in @($dataFile, $capacityFile, $wsdiFile, $renderer) + $stages.Script) {
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
    (Join-Path $ProjectRoot 'baseline\stata_outputs\layer2_a_country_distribution.csv'),
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
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\theta_distribution_cutoff_plot_data.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\theta_country_rank_plot_data.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\mA_by_debt_wsdi_plot_data.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_marginal_curve_debt.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_marginal_curve_ready_debt_cutoff.csv')
)
foreach ($path in $requiredOutputs) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Required machine-readable output missing or empty: $path"
    }
}

# Sections 2--3 use the requested LSDVC bootstrap configuration; Section 4
# retains country-clustered TWFE. Samples remain model-specific complete cases.
$baselineStats = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\model_stats.csv'))
$thetaStats = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_stats.csv'))
$doomStats = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_stats.csv'))
foreach ($row in ($baselineStats + $thetaStats)) {
    if ($row.estimator -ne 'LSDVC' -or $row.initial_estimator -ne 'Blundell-Bond' -or
        [int][double]$row.bias_order -ne 2 -or [int][double]$row.bootstrap_reps -ne 50 -or
        $row.se_type -ne 'bootstrap' -or [int][double]$row.country_fe -ne 1 -or
        [int][double]$row.year_fe -ne 1) {
        throw "Model $($row.model) does not report the required LSDVC/BB/bias(2)/bootstrap(50) configuration."
    }
}

# Fail closed before estimation if the delivered capacity join is not a unique,
# value-preserving iso3-year left join from the ND-GAIN wide source.
$capacitySourceRows = @(Import-Csv -LiteralPath $capacityFile)
if ($capacitySourceRows.Count -ne @($capacitySourceRows.ISO3 | Sort-Object -Unique).Count) {
    throw 'ND-GAIN capacity source contains duplicate ISO3 rows.'
}
$capacityByKey = @{}
foreach ($row in $capacitySourceRows) {
    foreach ($year in 1995..2023) {
        $rawValue = $row."$year"
        if (-not [string]::IsNullOrWhiteSpace($rawValue)) {
            $value = [double]$rawValue
            if ([double]::IsNaN($value) -or [double]::IsInfinity($value) -or $value -lt 0 -or $value -gt 1) {
                throw "Invalid ND-GAIN capacity value at $($row.ISO3) $year`: $rawValue"
            }
            $capacityByKey["$($row.ISO3)|$year"] = $value
        }
    }
}
$inputPanel = @(Import-Csv -LiteralPath $dataFile)
if (-not ($inputPanel[0].PSObject.Properties.Name -contains 'capacity')) {
    throw 'Main panel is missing the capacity column.'
}
$inputPanelKeys = @($inputPanel | ForEach-Object { "$($_.iso3)|$($_.year)" })
if ($inputPanel.Count -ne @($inputPanelKeys | Sort-Object -Unique).Count) {
    throw 'Main panel contains duplicate iso3-year keys.'
}
$capacityMatchedRows = 0
foreach ($row in $inputPanel) {
    $key = "$($row.iso3)|$($row.year)"
    $actualPresent = -not [string]::IsNullOrWhiteSpace($row.capacity)
    $expectedPresent = $capacityByKey.ContainsKey($key)
    if ($actualPresent -ne $expectedPresent) {
        throw "Capacity missingness does not match the source at $key."
    }
    if ($expectedPresent) {
        if ([math]::Abs(([double]$row.capacity) - $capacityByKey[$key]) -gt 1e-15) {
            throw "Capacity value differs from the source at $key."
        }
        $capacityMatchedRows++
    }
}
if ($capacityMatchedRows -ne 1769) {
    throw "Unexpected capacity coverage in the main panel: $capacityMatchedRows; expected 1769."
}
foreach ($row in $doomStats) {
    if ($row.cluster_variable -ne 'country_id' -or [int][double]$row.clusters -lt 2) {
        throw "Model $($row.model) does not report valid country_id-clustered inference."
    }
}
$spreadPreferred = @($thetaStats | Where-Object { $_.model -eq 'Spread_Interact_all' })
$taxPreferred = @($thetaStats | Where-Object { $_.model -eq 'T10_interact_full' })
$debtPreferred = @($doomStats | Where-Object { $_.model -eq 'DN3_full' })
if ($spreadPreferred.Count -ne 1 -or $taxPreferred.Count -ne 1 -or $debtPreferred.Count -ne 1) {
    throw 'Preferred upstream or DN3_full model statistics are missing or duplicated.'
}
if ([double]$debtPreferred[0].N -gt [double]$spreadPreferred[0].N -or [double]$debtPreferred[0].N -gt [double]$taxPreferred[0].N) {
    throw 'DN3_full cannot exceed either preferred upstream source regression sample.'
}

$thetaPanel = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\empirical_theta_panel.csv'))
$doomPanel = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop_nostate_panel.csv'))
foreach ($field in @('sample_spread', 'sample_tax', 'sample_theta_support', 'theta_constructible')) {
    if (-not ($thetaPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Empirical-theta panel is missing a required equation-support flag: $field"
    }
}
foreach ($field in @('capacity', 'adapt_capacity')) {
    if (-not ($thetaPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Empirical-theta panel is missing the A-construction field: $field"
    }
}
foreach ($field in @('sample_debt_ns', 'sample_ready_ns')) {
    if (-not ($doomPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Doomloop panel is missing a required full-equation sample flag: $field"
    }
}
foreach ($field in @('capacity', 'adapt_capacity')) {
    if (-not ($doomPanel[0].PSObject.Properties.Name -contains $field)) {
        throw "Doomloop panel is missing the A-construction field: $field"
    }
}

foreach ($panel in @($thetaPanel, $doomPanel)) {
    foreach ($row in $panel) {
        $capacityPresent = -not [string]::IsNullOrWhiteSpace($row.capacity) -and $row.capacity -ne '.'
        $adaptPresent = -not [string]::IsNullOrWhiteSpace($row.adapt_capacity) -and $row.adapt_capacity -ne '.'
        if ($capacityPresent -ne $adaptPresent) {
            throw "A and capacity missingness differ at $($row.iso3) $($row.year)."
        }
        if ($capacityPresent -and [math]::Abs(([double]$row.adapt_capacity) - (1.0-[double]$row.capacity)) -gt 1e-12) {
            throw "A is not exactly 1-capacity at $($row.iso3) $($row.year)."
        }
    }
}

foreach ($row in $thetaPanel) {
    $bPresent = -not [string]::IsNullOrWhiteSpace($row.b_pre) -and $row.b_pre -ne '.'
    $spreadSourceSample = $row.sample_spread -eq '1'
    $taxSourceSample = $row.sample_tax -eq '1'
    $mAPresent = -not [string]::IsNullOrWhiteSpace($row.mA_hat) -and $row.mA_hat -ne '.'
    $taPresent = -not [string]::IsNullOrWhiteSpace($row.TA_hat) -and $row.TA_hat -ne '.'
    $thetaPresent = -not [string]::IsNullOrWhiteSpace($row.theta_hat_A) -and $row.theta_hat_A -ne '.'
    if ($mAPresent -ne $spreadSourceSample) {
        throw "mA_hat availability does not match the Spread_Interact_all source sample at $($row.iso3) $($row.year)."
    }
    if ($taPresent -ne $taxSourceSample) {
        throw "TA_hat availability does not match the T10_interact_full source sample at $($row.iso3) $($row.year)."
    }
    $jointSupport = $bPresent -and $spreadSourceSample -and $taxSourceSample
    if ($thetaPresent -ne $jointSupport -or (($row.theta_constructible -eq '1') -ne $jointSupport) -or (($row.sample_theta_support -eq '1') -ne $jointSupport)) {
        throw "theta must be restricted to the joint preferred-source sample at $($row.iso3) $($row.year)."
    }
}

$thetaByKey = @{}
foreach ($row in $thetaPanel) {
    $thetaByKey["$($row.iso3)|$($row.year)"] = $row
}
foreach ($row in $doomPanel) {
    if ($row.sample_debt_ns -eq '1' -or $row.sample_ready_ns -eq '1') {
        $key = "$($row.iso3)|$($row.year)"
        if (-not $thetaByKey.ContainsKey($key)) {
            throw "Doomloop sample key is absent from the upstream theta panel: $key"
        }
        $source = $thetaByKey[$key]
        if ($source.sample_spread -ne '1' -or $source.sample_tax -ne '1') {
            throw "Doomloop sample lies outside a preferred upstream source regression: $key"
        }
    }
}

$layer2Distribution = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\layer2_a_country_distribution.csv'))
$layer2Stats = $baselineStats | Where-Object { $_.model -eq 'Layer2_A' }
if (@($layer2Stats).Count -ne 1 -or ($layer2Distribution | Measure-Object -Property observations -Sum).Sum -ne [double]$layer2Stats.N) {
    throw 'Layer2_A country distribution does not reconcile to the reported model sample.'
}

$thetaPlotRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\theta_distribution_cutoff_plot_data.csv'))
$thetaRankRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\theta_country_rank_plot_data.csv'))
$mAPlotRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\mA_by_debt_wsdi_plot_data.csv'))
$baselineMarginalRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'baseline\stata_outputs\marginal_effects.csv'))
$plotCutoffRows = @(Import-Csv -LiteralPath (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoffs.csv'))
if ($plotCutoffRows.Count -ne 1 -or $thetaPlotRows.Count -ne [int][double]$debtPreferred[0].N) {
    throw 'Theta distribution plot data must equal the DN3_full debt-equation sample and use its unique cutoff.'
}
$thetaPlotCountries = @($thetaPlotRows.iso3 | Sort-Object -Unique)
if ($thetaRankRows.Count -ne $thetaPlotCountries.Count -or @($thetaRankRows.iso3 | Sort-Object -Unique).Count -ne $thetaPlotCountries.Count) {
    throw 'Theta country-rank plot data do not reconcile to the distribution sample.'
}
foreach ($row in $thetaPlotRows) {
    if ([math]::Abs(([double]$row.cutoff) - ([double]$plotCutoffRows[0].rss_min_cutoff)) -gt 1e-12) {
        throw 'Theta distribution plot data use a cutoff inconsistent with the debt equation.'
    }
}
$plotPoints = @('P10', 'P25', 'P50', 'P75', 'P90')
if ($mAPlotRows.Count -ne 10) {
    throw 'mA moderator plot data must contain five debt and five WSDI percentile points.'
}
foreach ($row in $mAPlotRows) {
    $source = @($baselineMarginalRows | Where-Object {
        $_.model -eq 'Interact_all' -and $_.moderator -eq $row.moderator -and $_.point -eq $row.point
    })
    if ($source.Count -ne 1 -or -not ($plotPoints -contains $row.point)) {
        throw "mA plot row lacks a unique Interact_all source: $($row.moderator) $($row.point)"
    }
    if ([math]::Abs(([double]$row.mA) + ([double]$source[0].marginal_effect)) -gt 1e-8 -or
        [math]::Abs(([double]$row.ci_low) + ([double]$source[0].ci_high)) -gt 1e-8 -or
        [math]::Abs(([double]$row.ci_high) + ([double]$source[0].ci_low)) -gt 1e-8 -or
        $row.inference -ne 'LSDVC bootstrap VCE (50 reps)') {
        throw "mA plot transformation failed for $($row.moderator) $($row.point)."
    }
}

$copyStep = $stages.Count + 1
Write-Host "[$copyStep/$totalSteps] Copying current main-specification figure assets..."
if (-not (Test-Path -LiteralPath $figureSource -PathType Container)) {
    throw "Figure source directory not found: $figureSource"
}
New-Item -ItemType Directory -Force -Path $figureTarget | Out-Null
$requiredFigures = @(
    'figure1_theta_distribution_cutoff.png',
    'figure1_theta_distribution_cutoff.pdf',
    'figure2_mA_by_debt_wsdi.png',
    'figure2_mA_by_debt_wsdi.pdf',
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
    'T_{it}=\frac{(ConstantGDP_{it})}{(ConstantGDP_{i,t-1})}',
    'T_{i,t+1}=\frac{(ConstantGDP_{i,t+1})}{(ConstantGDP_{it})}=F.T_{it}',
    'X_{it}=wsdi\_days_{it}\times0.01',
    'A_{it}=1-Capacity_{it}',
    '\rho_s s_{i,t-1}',
    'b^{pre}_{it}=b_{i,t-1}=debt\_gdp_{i,t-1}',
    '不控制 $\ln(ConstantGDP)$',
    'T 指标方程的宏观控制仅为 Inflation，不控制 Growth',
    '\widehat\theta^A_{it}=b^{pre}_{it}\widehat m^A_{it}+\widehat T^A_{it}',
    '\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}',
    'A_{it}-A_{i,t-1}=\alpha_i+\lambda_t',
    '\beta_LA_{it}(c-\widehat\theta^A_{it})_+',
    '\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+',
    'Criterion Decomposition / Competing Criterion Test',
    '| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N | N_low | N_high |'
)) {
    if (-not $resultsText.Contains($requiredText)) {
        throw "Required formula or table text missing from integrated results: $requiredText"
    }
}

$diagnosticsText = Get-Content -Raw -LiteralPath $diagnosticsFile -Encoding UTF8
foreach ($requiredText in @(
    'Distribution of country or region samples — Layer2_A',
    '`vce(cluster country_id)`',
    'mA_hat 仅在 Spread_Interact_all 的实际样本内生成'
)) {
    if (-not $diagnosticsText.Contains($requiredText)) {
        throw "Required diagnostics text missing: $requiredText"
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
if ($resultsText.Contains('T_{it}=\frac{\ln(ConstantGDP_{it})}{\ln(ConstantGDP_{i,t-1})}')) {
    throw 'Obsolete log-ratio T formula remains in integrated results.'
}

foreach ($path in @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\unit_scaling_checks.csv')
)) {
    $wsdiRows = @(Import-Csv -LiteralPath $path | Where-Object { $_.variable -eq 'wsdi_days' })
    if ($wsdiRows.Count -ne 1 -or $wsdiRows[0].passed -ne '1' -or [math]::Abs([double]$wsdiRows[0].max_abs_scaling_diff) -gt 1e-12) {
        throw "WSDI scaling audit must contain one passing wsdi_days * 0.01 row: $path"
    }
    $capacityRows = @(Import-Csv -LiteralPath $path | Where-Object { $_.variable -eq 'adapt_capacity' })
    if ($capacityRows.Count -ne 1 -or $capacityRows[0].passed -ne '1' -or [math]::Abs([double]$capacityRows[0].max_abs_scaling_diff) -gt 1e-12) {
        throw "A construction audit must contain one passing adapt_capacity = 1-capacity row: $path"
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
$baselineRawAModels = @('A_A_only', 'B_all_core', 'C_macro', 'Layer2_A')
foreach ($model in $baselineRawAModels) {
    if (@($baselineCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'adapt_capacity' }).Count -ne 1) {
        throw "Baseline model $model must use adapt_capacity as A."
    }
}
if (@($baselineCoefficientRows | Where-Object { $_.variable -eq 'readiness100' }).Count -gt 0) {
    throw 'A Baseline model still uses readiness100 as A.'
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
$taxRawAModels = @('T2_A_only', 'T4_all_core', 'T5_macro', 'T7_layer2_A')
foreach ($model in $taxRawAModels) {
    if (@($taxCoefficientRows | Where-Object { $_.model -eq $model -and $_.variable -eq 'adapt_capacity' }).Count -ne 1) {
        throw "T-indicator model $model must use adapt_capacity as A."
    }
}
if (@($taxCoefficientRows | Where-Object { $_.variable -eq 'readiness100' }).Count -gt 0) {
    throw 'An empirical-theta model still uses readiness100 as A.'
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
foreach ($row in $criterionRows) {
    foreach ($field in @('cutoff','beta_L','p_L','beta_H','p_H','rss','r2_within','N','N_low','N_high','clusters')) {
        if ([string]::IsNullOrWhiteSpace($row.$field) -or $row.$field -eq '.') {
            throw "Criterion $($row.criterion) has a missing $field."
        }
    }
    $pL = [double]$row.p_L
    $pH = [double]$row.p_H
    if ($pL -lt 0 -or $pL -gt 1 -or $pH -lt 0 -or $pH -gt 1) {
        throw "Criterion $($row.criterion) has an invalid p-value."
    }
    if ([double]$row.rss -lt 0 -or [double]$row.N -le 0) {
        throw "Criterion $($row.criterion) has invalid RSS or sample size."
    }
    if ($row.cluster_variable -ne 'country_id' -or [int][double]$row.clusters -lt 2) {
        throw "Criterion $($row.criterion) does not report valid country-clustered inference."
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
