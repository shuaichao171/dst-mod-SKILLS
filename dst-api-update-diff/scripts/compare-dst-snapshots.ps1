[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OldSnapshot,
    [Parameter(Mandatory = $true)]
    [string]$NewSnapshot,
    [string]$OutputPath
)

$old = Get-Content -Raw -Encoding UTF8 -LiteralPath $OldSnapshot -ErrorAction Stop | ConvertFrom-Json
$new = Get-Content -Raw -Encoding UTF8 -LiteralPath $NewSnapshot -ErrorAction Stop | ConvertFrom-Json

function ConvertTo-FileMap {
    param(
        [object]$Snapshot,
        [string]$Label
    )

    if ($null -eq $Snapshot -or $Snapshot.schema_version -isnot [int] -or
        $Snapshot.schema_version -ne 1 -or
        $Snapshot.files -isnot [System.Array]) {
        throw ($Label + ' snapshot must use schema_version 1 and contain a files array.')
    }
    if ($Snapshot.file_count -isnot [int] -or
        $Snapshot.file_count -ne $Snapshot.files.Count) {
        throw ($Label + ' snapshot file_count does not match the files array.')
    }

    $byPath = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($file in $Snapshot.files) {
        if ($null -eq $file -or $file.path -isnot [string] -or
            [string]::IsNullOrWhiteSpace($file.path)) {
            throw ($Label + ' snapshot contains a file with an invalid path.')
        }
        if ($file.sha256 -isnot [string] -or
            $file.sha256 -notmatch '^[0-9A-Fa-f]{64}$') {
            throw ($Label + ' snapshot contains an invalid SHA-256 for: ' + $file.path)
        }
        if ($byPath.ContainsKey($file.path)) {
            throw ($Label + ' snapshot contains a duplicate path: ' + $file.path)
        }
        $byPath[$file.path] = $file
    }

    return $byPath
}

$oldByPath = ConvertTo-FileMap $old 'Old'
$newByPath = ConvertTo-FileMap $new 'New'

$paths = [System.Collections.Generic.SortedSet[string]]::new(
    [System.StringComparer]::Ordinal
)
foreach ($path in $oldByPath.Keys) {
    [void]$paths.Add($path)
}
foreach ($path in $newByPath.Keys) {
    [void]$paths.Add($path)
}
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
    if ($changes.Count -eq 0) {
        Write-Host 'No file changes.'
    }
    else {
        $changes
    }
}
else {
    $fullOutput = [System.IO.Path]::GetFullPath($OutputPath)
    if ([System.IO.Path]::GetExtension($fullOutput) -ine '.json') {
        throw ('Output path must use a .json extension: ' + $fullOutput)
    }
    $oldFullPath = (Resolve-Path -LiteralPath $OldSnapshot).Path
    $newFullPath = (Resolve-Path -LiteralPath $NewSnapshot).Path
    if ($fullOutput -ieq $oldFullPath -or $fullOutput -ieq $newFullPath) {
        throw 'Output path must not overwrite an input snapshot.'
    }
    $parent = Split-Path -Parent $fullOutput
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $report = [ordered]@{
        schema_version = 1
        old_snapshot = $oldFullPath
        new_snapshot = $newFullPath
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
