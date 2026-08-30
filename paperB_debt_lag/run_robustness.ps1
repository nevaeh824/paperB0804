[CmdletBinding()]
param(
    [string]$ProjectRoot = '',
    [string]$StataExe = 'C:\Environment_tools\Stata18\StataMP-64.exe',
    [switch]$SkipBootstrap
)

$ErrorActionPreference = 'Stop'
$workflowRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $workflowRoot
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$currentRoot = Join-Path $ProjectRoot 'paperB\paperBresult'
$laggedRoot = Join-Path $ProjectRoot 'paperB_debt_lag\paperB_debt_lag'
$robustRoot = Join-Path $currentRoot 'robustness'
$comparisonPy = Join-Path $workflowRoot 'compare_debt_timing.py'
$comparisonDo = Join-Path $workflowRoot 'code\comparison_experiments.do'
$bootstrapDo = Join-Path $workflowRoot 'code\bootstrap_full_pipeline.do'
$draws = Join-Path $robustRoot 'country_bootstrap_draw_assignments.csv'

foreach ($path in @($currentRoot, $laggedRoot)) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        throw "Run both main workflows before robustness: $path"
    }
}
foreach ($path in @($comparisonPy, $comparisonDo, $bootstrapDo, $StataExe)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required robustness program not found: $path"
    }
}
New-Item -ItemType Directory -Force -Path $robustRoot | Out-Null

$script:py = Get-Command py -ErrorAction SilentlyContinue
function Invoke-Python {
    param([string[]]$Arguments)
    if ($null -ne $script:py) {
        & $script:py.Source -3.14 @Arguments
    }
    else {
        $python = Get-Command python -ErrorAction Stop
        & $python.Source @Arguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Python robustness command failed with code $LASTEXITCODE"
    }
}

function Invoke-StataDo {
    param(
        [string]$Script,
        [string[]]$DoArguments,
        [string]$Log,
        [string]$Marker
    )
    $scriptStata = (Resolve-Path -LiteralPath $Script).Path.Replace('\', '/')
    $stataArguments = @('/e', 'do', "`"$scriptStata`"")
    foreach ($argument in $DoArguments) {
        $stataArguments += "`"$($argument.Replace('\', '/'))`""
    }
    $process = Start-Process -FilePath $StataExe -ArgumentList $stataArguments `
        -WorkingDirectory $ProjectRoot -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $Log -PathType Leaf)) {
        throw "Stata robustness stage failed before log validation: $Script"
    }
    $logText = Get-Content -Raw -Encoding UTF8 -LiteralPath $Log
    if (-not $logText.Contains($Marker) -or $logText -match '(?m)^r\([0-9]+\);\s*$') {
        throw "Stata robustness log failed validation: $Log"
    }
}

Write-Host '[1/6] Preparing standardized RSS profiles and paired country draws...'
Invoke-Python @($comparisonPy, '--project-root', $ProjectRoot, '--stage', 'prepare')

Write-Host '[2/6] Estimating fixed-cutoff and common-742 comparisons...'
Invoke-StataDo -Script $comparisonDo `
    -DoArguments @($ProjectRoot, $currentRoot, $laggedRoot, $robustRoot) `
    -Log (Join-Path $robustRoot 'comparison_experiments.log') `
    -Marker 'COMPARISON EXPERIMENTS COMPLETE'

Write-Host '[3/6] Running paired 30-replication country bootstrap...'
if (-not $SkipBootstrap) {
    Invoke-StataDo -Script $bootstrapDo `
        -DoArguments @($ProjectRoot, $draws, $robustRoot, '30') `
        -Log (Join-Path $robustRoot 'country_bootstrap.log') `
        -Marker 'COUNTRY BOOTSTRAP COMPLETE'
}
elseif (-not (Test-Path -LiteralPath (Join-Path $robustRoot 'country_bootstrap_replications.csv') -PathType Leaf)) {
    throw 'SkipBootstrap requires an existing country_bootstrap_replications.csv.'
}

Write-Host '[4/6] Summarizing and synchronizing robustness artifacts...'
Invoke-Python @($comparisonPy, '--project-root', $ProjectRoot, '--stage', 'summarize')
Invoke-Python @($comparisonPy, '--project-root', $ProjectRoot, '--stage', 'copy')

Write-Host '[5/6] Rendering robustness figures and supplemented documents...'
$jobs = @(
    @((Join-Path $ProjectRoot 'paperB\render_figures.py'), $currentRoot, (Join-Path $currentRoot 'figures'), (Join-Path $ProjectRoot 'paperB\render_output.py')),
    @((Join-Path $ProjectRoot 'paperB_debt_lag\render_figures.py'), $laggedRoot, (Join-Path $laggedRoot 'figures'), (Join-Path $ProjectRoot 'paperB_debt_lag\render_output.py'))
)
foreach ($job in $jobs) {
    Invoke-Python @($job[0], '--project-root', $job[1], '--output-dir', $job[2])
    Invoke-Python @($job[3])
}

Write-Host '[6/6] Validating paired output coverage...'
$replications = @(Import-Csv -LiteralPath (Join-Path $robustRoot 'country_bootstrap_replications.csv'))
$common = @(Import-Csv -LiteralPath (Join-Path $robustRoot 'common_742_specification.csv'))
$cross = @(Import-Csv -LiteralPath (Join-Path $robustRoot 'cross_cutoff_sensitivity.csv'))
if ($replications.Count -ne 60) {
    throw 'Bootstrap output must contain 60 specification-replication rows.'
}
foreach ($specification in @('current_debt', 'lagged_debt')) {
    $group = @($replications | Where-Object specification -eq $specification)
    $replicateIds = @($group | ForEach-Object { [int]$_.replicate } | Sort-Object -Unique)
    $valid = @($group | Where-Object status -eq 'success')
    if ($group.Count -ne 30 -or $replicateIds.Count -ne 30 -or $valid.Count -lt 1) {
        throw "Bootstrap output lacks paired coverage or a valid draw for $specification."
    }
}
if ($common.Count -ne 2 -or @($common | Where-Object { [int][double]$_.N -ne 742 }).Count -ne 0) {
    throw 'Common-sample output must contain two N=742 rows.'
}
if ($cross.Count -ne 4) {
    throw 'Cross-cutoff output must contain four rows.'
}
Write-Host 'Paper B debt-timing robustness workflow complete.'
Write-Host "Current results: $currentRoot"
Write-Host "Lagged results: $laggedRoot"
