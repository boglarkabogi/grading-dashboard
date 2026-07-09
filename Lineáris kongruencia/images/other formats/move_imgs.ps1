$target = Join-Path $PSScriptRoot "IMAGES"

if (!(Test-Path $target)) {
    New-Item -ItemType Directory -Path $target | Out-Null
}

Get-ChildItem -Path $PSScriptRoot -File |
Where-Object {
    $_.Extension.ToLower() -in ".jpg", ".jpeg", ".png"
} |
Move-Item -Destination $target -Force

Write-Host "Kész, a képek át lettek mozgatva az IMAGES mappába."
Read-Host "Enter a kilépéshez"