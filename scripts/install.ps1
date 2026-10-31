<#
.SYNOPSIS
  Install selected AI Dev Assistant features into another repository without Python.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Target "C:\Projects\MyApp" -All
.EXAMPLE
  .\scripts\install.ps1 -Target "C:\Projects\MyApp" -Features logging-advisor,code-review
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)] [string] $Target,
    [Parameter(Mandatory = $false)] [string[]] $Features,
    [Parameter(Mandatory = $false)] [switch] $All,
    [Parameter(Mandatory = $false)] [switch] $List,
    [Parameter(Mandatory = $false)] [switch] $DryRun,
    [Parameter(Mandatory = $false)] [switch] $Overwrite
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ManifestPath = Join-Path $Root 'manifest\features.json'
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    throw "Feature manifest not found: $ManifestPath"
}
function ConvertTo-Hashtable($Value) {
    if ($Value -is [System.Management.Automation.PSCustomObject]) {
        $Result = @{}
        foreach ($Property in $Value.PSObject.Properties) {
            $Result[$Property.Name] = ConvertTo-Hashtable $Property.Value
        }
        return $Result
    }
    if ($Value -is [System.Array]) {
        return ,@($Value | ForEach-Object { ConvertTo-Hashtable $_ })
    }
    return $Value
}
function Get-TargetRelativePath([string] $FullPath, [string] $BasePath) {
    $Prefix = $BasePath.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if ($FullPath.StartsWith($Prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $FullPath.Substring($Prefix.Length)
    }
    return $FullPath
}
$Manifest = ConvertTo-Hashtable (Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json)
$FeatureMap = $Manifest.features

if ($List) {
    foreach ($Name in $FeatureMap.Keys) {
        Write-Output ("{0,-28} {1}" -f $Name, $FeatureMap[$Name].description)
    }
    exit 0
}
if (-not $Target) { throw 'Specify -Target unless using -List.' }
if (-not $All -and (-not $Features -or $Features.Count -eq 0)) {
    throw 'Choose -All or provide -Features feature-id,feature-id.'
}
if ($All -and $Features) { throw 'Use either -All or -Features, not both.' }

$Selected = if ($All) { @($FeatureMap.Keys) } else { @($Features) }
foreach ($Name in $Selected) {
    if (-not $FeatureMap.ContainsKey($Name)) {
        throw "Unknown feature '$Name'. Run with -List to see valid feature IDs."
    }
}

$TargetFull = [System.IO.Path]::GetFullPath($Target)
$RootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\')
if (-not (Test-Path -LiteralPath $TargetFull -PathType Container)) {
    throw "Target directory must already exist: $TargetFull"
}
if ($TargetFull.Equals($RootFull, [System.StringComparison]::OrdinalIgnoreCase) -or
    $TargetFull.StartsWith($RootFull + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Target cannot be the toolkit repository itself or one of its subdirectories.'
}

$Copied = 0
$Skipped = 0
foreach ($Name in $Selected) {
    $Feature = $FeatureMap[$Name]
    Write-Output "`n[$Name] $($Feature.description)"
    foreach ($Entry in $Feature.files) {
        $Source = [System.IO.Path]::GetFullPath((Join-Path $Root $Entry.source))
        $SourcePrefix = $RootFull + '\'
        if (-not $Source.StartsWith($SourcePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Invalid source path in manifest: $($Entry.source)"
        }
        $Destination = [System.IO.Path]::GetFullPath((Join-Path $TargetFull $Entry.destination))
        if (-not $Destination.StartsWith(($TargetFull.TrimEnd('\') + '\'), [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Invalid destination path in manifest: $($Entry.destination)"
        }

        if ($Entry.kind -eq 'directory') {
            if (-not (Test-Path -LiteralPath $Source -PathType Container)) { throw "Source directory missing: $Source" }
            $Files = Get-ChildItem -LiteralPath $Source -File -Recurse | Where-Object {
                $_.FullName -notmatch '[\\/](__pycache__)[\\/]' -and $_.Extension -notin @('.pyc', '.pyo') -and $_.Name -ne '.DS_Store'
            }
            foreach ($File in $Files) {
                $Relative = $File.FullName.Substring($Source.Length).TrimStart('\', '/')
                $DestFile = Join-Path $Destination $Relative
                if ((Test-Path -LiteralPath $DestFile) -and -not $Overwrite) {
                    Write-Output "  SKIP existing: $((Get-TargetRelativePath $DestFile $TargetFull))"
                    $Skipped++
                    continue
                }
                Write-Output ("  {0}: {1} -> {2}" -f $(if ($DryRun) { 'WOULD COPY' } else { 'COPY' }), "$($Entry.source)/$Relative", (Get-TargetRelativePath $DestFile $TargetFull))
                if (-not $DryRun) {
                    $Parent = Split-Path -Parent $DestFile
                    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
                    Copy-Item -LiteralPath $File.FullName -Destination $DestFile -Force:$Overwrite
                }
                $Copied++
            }
        }
        elseif ($Entry.kind -eq 'file') {
            if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Source file missing: $Source" }
            if ((Test-Path -LiteralPath $Destination) -and -not $Overwrite) {
                Write-Output "  SKIP existing: $($Entry.destination)"
                $Skipped++
                continue
            }
            Write-Output ("  {0}: {1} -> {2}" -f $(if ($DryRun) { 'WOULD COPY' } else { 'COPY' }), $Entry.source, $Entry.destination)
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
                Copy-Item -LiteralPath $Source -Destination $Destination -Force:$Overwrite
            }
            $Copied++
        }
        else { throw "Unknown manifest entry kind '$($Entry.kind)' for $($Entry.source)" }
    }
}
$Verb = if ($DryRun) { 'Would copy' } else { 'Copied' }
Write-Output "`nCompleted. $Verb`: $Copied; skipped: $Skipped."
if (-not $DryRun) { Write-Output 'Review the changed files and commit them through your normal code-review process.' }
