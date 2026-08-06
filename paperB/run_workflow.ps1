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
    foreach ($line in Get-Content -LiteralPath $path -Encoding UTF8 | Where-Object { $_ -match '^\|' }) {
        $count = ([regex]::Matches($line, '(?<!\\)\|')).Count
        if ($count -lt 2) {
            throw "Malformed Markdown table row in $path`: $line"
        }
    }
}

$resultsText = Get-Content -Raw -LiteralPath $resultsFile -Encoding UTF8
foreach ($requiredText in @(
    '\widetilde T_{i,t+1}^{(t)}=\frac{(taxgdp_{i,t+1}\times0.01)\,CurrentGDP_{i,t+1}}{CurrentGDP_{it}}',
    '\widetilde T_{it}^{(t-1)}=taxgdp_{it}\times0.01',
    '\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat T^A_{it}',
    'b_{it}=debt\_gdp_{it}',
    '\delta_LFT_{it}(c-\widehat\theta^A_{it})_+',
    '\delta_HFT_{it}(\widehat\theta^A_{it}-c)_+'
)) {
    if (-not $resultsText.Contains($requiredText)) {
        throw "Required formula text missing from integrated results: $requiredText"
    }
}

$validationFiles = @(
    (Join-Path $ProjectRoot 'baseline\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'empirical_theta\stata_outputs\formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\unit_scaling_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_formula_checks.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\cutoff_validation.csv'),
    (Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_cutoff_validation.csv')
)
foreach ($path in $validationFiles) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Validation output not found: $path"
    }
    $failed = @(Import-Csv -LiteralPath $path | Where-Object { $_.passed -ne '1' })
    if ($failed.Count -gt 0) {
        throw "Validation failure recorded in $path"
    }
}

$taxCoefficientFile = Join-Path $ProjectRoot 'empirical_theta\stata_outputs\model_coefficients.csv'
$doomCoefficientFile = Join-Path $ProjectRoot 'doomloop\stata_outputs\model_coefficients.csv'
$noStateCoefficientFile = Join-Path $ProjectRoot 'doomloop\stata_outputs\nostate_model_coefficients.csv'
$taxCoefficientRows = Import-Csv -LiteralPath $taxCoefficientFile
$doomCoefficientRows = Import-Csv -LiteralPath $doomCoefficientFile
$noStateCoefficientRows = Import-Csv -LiteralPath $noStateCoefficientFile
if (@($taxCoefficientRows | Where-Object { $_.model -like 'T*' -and $_.variable -eq 'ln_currentgdp' }).Count -gt 0) {
    throw 'Tax-base equation still contains ln_currentgdp.'
}
if (@($doomCoefficientRows | Where-Object { $_.model -like 'D*' -and $_.variable -eq 'ln_currentgdp' }).Count -gt 0) {
    throw 'Debt-change equation still contains ln_currentgdp.'
}
if (@($noStateCoefficientRows | Where-Object { $_.model -like 'DN*' -and $_.variable -eq 'ln_currentgdp' }).Count -gt 0) {
    throw 'No-b debt-change equation still contains ln_currentgdp.'
}

$requiredFigures = @(
    'debt_marginal_effect.png', 'debt_marginal_effect.pdf',
    'debt_marginal_effect_no_b.png', 'debt_marginal_effect_no_b.pdf',
    'readiness_marginal_effect.png', 'readiness_marginal_effect.pdf',
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
