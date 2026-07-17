[CmdletBinding()]
param(
    [string]$Root = 'D:\steam\steamapps\common\Don''t Starve Together\data\scripts',
    [ValidateSet('Summary', 'Files', 'Symbol')]
    [string]$Mode = 'Summary',
    [string]$Pattern,
    [string]$Glob = '*.lua'
)

$resolvedRoot = (Resolve-Path -LiteralPath $Root -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot 'main.lua') -PathType Leaf)) {
    throw ('The root does not look like a DST data/scripts directory: ' + $resolvedRoot)
}

switch ($Mode) {
    'Summary' {
        Get-ChildItem -LiteralPath $resolvedRoot -Directory |
            ForEach-Object {
                [pscustomobject]@{
                    Module = $_.Name
                    LuaFiles = (Get-ChildItem -LiteralPath $_.FullName -Recurse -File -Filter '*.lua').Count
                }
            } |
            Sort-Object LuaFiles -Descending

        [pscustomobject]@{
            Module = '(root)'
            LuaFiles = (Get-ChildItem -LiteralPath $resolvedRoot -File -Filter '*.lua').Count
        }
    }

    'Files' {
        Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter $Glob |
            Sort-Object FullName |
            Select-Object -ExpandProperty FullName
    }

    'Symbol' {
        if ([string]::IsNullOrWhiteSpace($Pattern)) {
            throw '-Pattern is required when -Mode Symbol is used.'
        }

        $rg = Get-Command rg -ErrorAction SilentlyContinue
        if ($null -ne $rg) {
            & $rg.Source -n --glob $Glob -- $Pattern $resolvedRoot
            if ($LASTEXITCODE -gt 1) {
                throw ('rg failed with exit code ' + $LASTEXITCODE)
            }
        }
        else {
            Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter $Glob |
                Select-String -Pattern $Pattern |
                ForEach-Object {
                    '{0}:{1}:{2}' -f $_.Path, $_.LineNumber, $_.Line.Trim()
                }
        }
    }
}

