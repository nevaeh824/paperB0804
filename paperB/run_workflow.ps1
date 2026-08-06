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
$stataBatchLog = Join-Path $ProjectRoot "$(Split-Path -Leaf $ProjectRoot).log"

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
        Name = 'doomloop'
        Script = Join-Path $codeRoot 'doomloop.do'
        Log = Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop.log'
        Marker = 'ANALYSIS COMPLETE'
    }
    [pscustomobject]@{
        Name = 'doomloop_no_state'
        Script = Join-Path $codeRoot 'doomloop_no_state.do'
        Log = Join-Path $ProjectRoot 'doomloop\stata_outputs\doomloop_no_state.log'
        Marker = 'ANALYSIS COMPLETE NO-STATE'
    }
)

foreach ($path in @($dataFile, $renderer) + $stages.Script) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required workflow input not found: $path"
    }
}

if (-not $SkipStata) {
    if (-not (Test-Path -LiteralPath $StataExe -PathType Leaf)) {
        throw "Stata executable not found: $StataExe"
    }
    if (Test-Path -LiteralPath $stataBatchLog) {
        throw "Reserved Stata batch log already exists; move it before running to avoid overwrite: $stataBatchLog"
    }

    $stageNumber = 1
    foreach ($stage in $stages) {
        Write-Host "[$stageNumber/7] Running $($stage.Name)..."
        $scriptStata = $stage.Script.Replace('\', '/')
        $process = Start-Process -FilePath $StataExe `
            -ArgumentList @('/e', 'do', "`"$scriptStata`"", "`"$projectRootStata`"") `
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
    if (Test-Path -LiteralPath $stataBatchLog -PathType Leaf) {
        Remove-Item -LiteralPath $stataBatchLog -Force
    }
}
else {
    Write-Host '[1/7] Skipping Stata estimation; validating existing machine-readable outputs...'
}

Write-Host '[5/7] Copying final figure assets...'
if (-not (Test-Path -LiteralPath $figureSource -PathType Container)) {
    throw "Figure source directory not found: $figureSource"
}
New-Item -ItemType Directory -Force -Path $figureTarget | Out-Null
Get-ChildItem -LiteralPath $figureSource -File | Where-Object { $_.Extension -in @('.png', '.pdf') } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $figureTarget $_.Name) -Force
}

Write-Host '[6/7] Rendering results, diagnostics, and progress documents...'
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

Write-Host '[7/7] Running integrated QA...'
foreach ($path in @($resultsFile, $diagnosticsFile, $progressFile)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Integrated document was not generated: $path"
    }
    $text = Get-Content -Raw -LiteralPath $path -Encoding UTF8
    if ($text -match 'PaperB_DoomLoop_') {
        throw "Forbidden draft reference found in $path"
    }
    if ($text -match 'ln_capitaGDP|lnrgdp|\\ln\(capitaGDP\)') {
        throw "Forbidden per-capita or legacy GDP log control found in $path"
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
    '\widetilde T_{i,t+1}^{(t)}=\frac{revenue_{i,t+1}}{CurrentGDP_{it}}',
    '\widetilde T_{it}^{(t-1)}=\frac{revenue_{it}}{CurrentGDP_{i,t-1}}',
    '\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat T^A_{it}',
    'b_{it}=\frac{debt_{it}}{CurrentGDP_{it}}',
    '\frac{1}{2}\beta_{AA}',
    '\widehat\beta_{AA}A_{it}',
    '\frac{1}{2}\gamma_{AA}',
    '\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AA}A_{it}+\widehat\gamma_{AX}X_{it}',
    '\phi_b b_{it}',
    'ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change',
    '\delta_LFT_{it}(c-\widehat\theta^A_{it})_+',
    '\delta_HFT_{it}(\widehat\theta^A_{it}-c)_+',
    'debt-equation cutoff'
)) {
    if (-not $resultsText.Contains($requiredText)) {
        throw "Required formula text missing from integrated results: $requiredText"
    }
}

$coefficientOutputs = @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\model_coefficients.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_coefficients.csv')
)
foreach ($path in $coefficientOutputs) {
    $text = Get-Content -Raw -LiteralPath $path -Encoding UTF8
    if ($text -match '(?m),(ln_capitaGDP|lnrgdp),') {
        throw "Forbidden per-capita or legacy GDP log coefficient found in $path"
    }
    if ($text -match '(?m),debt_gdp,') {
        throw "Legacy debt_gdp coefficient found in $path"
    }
    foreach ($requiredControl in @(',growth,', ',inflation_cpi,', ',reserves,', ',tt,')) {
        if (-not $text.Contains($requiredControl)) {
            throw "Required control $requiredControl missing from $path"
        }
    }
}

function Assert-LogControlAssignment {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$RequiredModels,
        [string[]]$ForbiddenModels = @()
    )
    $rows = @(Import-Csv -LiteralPath $Path -Encoding UTF8)
    foreach ($model in $RequiredModels) {
        $matches = @($rows | Where-Object { $_.model -eq $model -and $_.variable -eq 'ln_currentgdp' })
        if ($matches.Count -ne 1) {
            throw "Expected exactly one ln_currentgdp coefficient for $model in $Path; found $($matches.Count)"
        }
    }
    foreach ($model in $ForbiddenModels) {
        $matches = @($rows | Where-Object { $_.model -eq $model -and $_.variable -eq 'ln_currentgdp' })
        if ($matches.Count -ne 0) {
            throw "ln_currentgdp must be excluded from $model in $Path"
        }
    }
}

Assert-LogControlAssignment -Path $coefficientOutputs[0] `
    -RequiredModels @('A_X_only','A_A_only','A_b_only','B_all_core','C_macro','Layer1_X','Layer2_A','Interact_AB','Interact_AX','Interact_all','Quadratic_all')
Assert-LogControlAssignment -Path $coefficientOutputs[1] `
    -RequiredModels @('Spread_Quadratic_all') `
    -ForbiddenModels @('T1_X_only','T2_A_only','T3_persistence','T4_all_core','T5_macro','T6_layer1_X','T7_layer2_A','T8_interact_core','T9_interact_macro','T10_interact_full','T11_quadratic_full')
Assert-LogControlAssignment -Path $coefficientOutputs[2] `
    -RequiredModels @('R1_core','R2_macro','R3_full','RD1_debtcut','RD2_debtcut','RD3_debtcut') `
    -ForbiddenModels @('D1_core','D2_macro','D3_full')
Assert-LogControlAssignment -Path $coefficientOutputs[3] `
    -RequiredModels @('RN1_core','RN2_macro','RN3_full') `
    -ForbiddenModels @('DN1_core','DN2_macro','DN3_full')

$baselineCoefficientText = Get-Content -Raw -LiteralPath $coefficientOutputs[0] -Encoding UTF8
$doomCoefficientText = Get-Content -Raw -LiteralPath $coefficientOutputs[2] -Encoding UTF8
if (-not $baselineCoefficientText.Contains(',b_it,')) {
    throw 'Derived b_it=debt/CurrentGDP coefficient missing from baseline output'
}
if (-not $doomCoefficientText.Contains(',b_it_theta,')) {
    throw 'Derived b_it=debt/CurrentGDP coefficient missing from doomloop output'
}

$cutoffPath = Join-Path $ProjectRoot 'doomloop\stata_outputs\cutoffs.csv'
$scenarioPath = Join-Path $ProjectRoot 'doomloop\stata_outputs\readiness_cutoff_scenarios.csv'
$scenarioCheckPath = Join-Path $ProjectRoot 'doomloop\stata_outputs\cutoff_scenario_checks.csv'
$cutoffRows = @(Import-Csv -LiteralPath $cutoffPath -Encoding UTF8)
$scenarioRows = @(Import-Csv -LiteralPath $scenarioPath -Encoding UTF8)
$scenarioCheckRows = @(Import-Csv -LiteralPath $scenarioCheckPath -Encoding UTF8)
$debtCutoff = [double](($cutoffRows | Where-Object equation -eq 'debt').rss_min_cutoff)
$readyCutoff = [double](($cutoffRows | Where-Object equation -eq 'ready').rss_min_cutoff)
$ownScenario = $scenarioRows | Where-Object scenario -eq 'readiness_minRSS'
$debtScenario = $scenarioRows | Where-Object scenario -eq 'debt_equation_cutoff'
if (@($ownScenario).Count -ne 1 -or @($debtScenario).Count -ne 1) {
    throw 'Expected exactly two named readiness cutoff scenarios'
}
if ($ownScenario.cutoff_source -ne 'readiness_equation' -or $debtScenario.cutoff_source -ne 'debt_change_equation') {
    throw 'Readiness cutoff scenario provenance is incorrect'
}
if ([math]::Abs([double]$ownScenario.cutoff - $readyCutoff) -gt 1e-12 -or [math]::Abs([double]$debtScenario.cutoff - $debtCutoff) -gt 1e-12) {
    throw 'Readiness scenario cutoff does not match its declared source equation'
}
if ([double]$debtScenario.rss_gap -lt -1e-10) {
    throw 'Readiness RSS at the debt-equation cutoff is below the saved readiness minimum'
}
if ($scenarioCheckRows.Count -ne 3 -or @($scenarioCheckRows | Where-Object passed -ne '1').Count -ne 0) {
    throw 'Readiness cutoff scenario checks failed'
}

$requiredFigures = @(
    'debt_marginal_effect.png', 'debt_marginal_effect.pdf',
    'debt_marginal_effect_no_b.png', 'debt_marginal_effect_no_b.pdf',
    'readiness_marginal_effect.png', 'readiness_marginal_effect.pdf',
    'readiness_marginal_effect_debt_cutoff.png', 'readiness_marginal_effect_debt_cutoff.pdf',
    'readiness_cutoff_comparison.png', 'readiness_cutoff_comparison.pdf',
    'readiness_marginal_effect_no_lag.png', 'readiness_marginal_effect_no_lag.pdf',
    'kink_marginal_effects.png', 'kink_marginal_effects.pdf',
    'kink_marginal_effects_no_state.png', 'kink_marginal_effects_no_state.pdf'
)
foreach ($name in $requiredFigures) {
    $path = Join-Path $figureTarget $name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Required figure missing or empty: $path"
    }
}

Write-Host 'Paper B workflow complete.'
Write-Host "Results: $resultsFile"
Write-Host "Diagnostics: $diagnosticsFile"
Write-Host "Progress: $progressFile"
Write-Host "Workflow: $(Join-Path $paperRoot 'WORKFLOW.md')"
