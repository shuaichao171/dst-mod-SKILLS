[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OldSnapshot,
    [Parameter(Mandatory = $true)]
    [string]$NewSnapshot,
    [string]$OutputPath
)

$old = Get-Content -Raw -LiteralPath $OldSnapshot | ConvertFrom-Json
$new = Get-Content -Raw -LiteralPath $NewSnapshot | ConvertFrom-Json

$oldByPath = @{}
foreach ($file in $old.files) {
    $oldByPath[$file.path] = $file
}

$newByPath = @{}
foreach ($file in $new.files) {
    $newByPath[$file.path] = $file
}

$paths = @($oldByPath.Keys + $newByPath.Keys | Sort-Object -Unique)
$changes = @(
    foreach ($path in $paths) {
        $oldFile = $oldByPath[$path]
        $newFile = $newByPath[$path]

        if ($null -eq $oldFile) {
            [pscustomobject]@{ Status = 'Added'; Path = $path; OldHash = $null; NewHash = $newFile.sha256 }
        }
        elseif ($null -eq $newFile) {
            [pscustomobject]@{ Status = 'Removed'; Path = $path; OldHash = $oldFile.sha256; NewHash = $null }
        }
        elseif ($oldFile.sha256 -ne $newFile.sha256) {
            [pscustomobject]@{ Status = 'Changed'; Path = $path; OldHash = $oldFile.sha256; NewHash = $newFile.sha256 }
        }
    }
)

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $changes
}
else {
    $fullOutput = [System.IO.Path]::GetFullPath($OutputPath)
    $parent = Split-Path -Parent $fullOutput
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $report = [ordered]@{
        schema_version = 1
        old_snapshot = (Resolve-Path -LiteralPath $OldSnapshot).Path
        new_snapshot = (Resolve-Path -LiteralPath $NewSnapshot).Path
        added = @($changes | Where-Object Status -eq 'Added').Count
        removed = @($changes | Where-Object Status -eq 'Removed').Count
        changed = @($changes | Where-Object Status -eq 'Changed').Count
        files = $changes
    }

    $json = $report | ConvertTo-Json -Depth 6
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($fullOutput, $json, $encoding)
    Get-Item -LiteralPath $fullOutput
}

