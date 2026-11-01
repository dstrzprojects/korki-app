$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$link = $shell.CreateShortcut((Join-Path $desktop 'Lekcje.lnk'))
$link.TargetPath = Join-Path $root 'Uruchom.cmd'
$link.WorkingDirectory = $root
$link.Description = 'Lokalny dziennik lekcji i rozliczen'
$link.Save()
Write-Host 'Utworzono skrot Lekcje na pulpicie.'
