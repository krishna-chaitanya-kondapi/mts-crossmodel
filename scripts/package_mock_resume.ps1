param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$paths=@('AGENTS.md','constitution.md','requirements.txt','src','scripts','tests','specs','docs','data','workflows')
$files=foreach($relative in $paths) {
    $path=Join-Path $repo $relative
    if(Test-Path -LiteralPath $path) { $path }
}
Compress-Archive -LiteralPath $files -DestinationPath $Destination -Force
Write-Output "Created resume bundle $Destination"
