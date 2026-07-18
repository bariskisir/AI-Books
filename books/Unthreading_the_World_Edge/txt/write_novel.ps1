$path = "C:\Users\white\main\gitrepos\ai-books\books\Unthreading_the_World_Edge\txt\Unthreading_the_World_Edge.txt"

# Build complete novel line by line
$lines = @()
$lines += "Unthreading the World-Edge"
$lines += ""
$lines += "A Novel"
$lines += ""
$lines += "---"
$lines += ""
$lines += "ARC I: THE STITCH THAT HOLDS"
$lines += ""

# Chapter 1
$lines += "Chapter 1: The Last Good Thread"
$lines += ""
$lines += "Tessa Loom pulled her needle through the cloth and felt the world hold steady."
$lines += ""
$lines += "The motion was so familiar she barely saw it -- silver needle arcing up, thread following like a loyal thought, the whisper of fiber through fiber. Her fingers worked by memory while her eyes wandered to the window where the Wall stood against the sky."
$lines += ""
$lines += "The Wall was always there. Gray and seamless, it rose from the mountain's spine and climbed until it vanished into clouds that never cleared. Tessa had lived beneath it for twenty-two years. She had never seen the other side."
$lines += ""
$lines += ""Tessa!""
$lines += ""
$lines += "She blinked. Her mother stood in the workshop doorway, arms folded."
$lines += ""
$lines += ""You've been staring at that seam for an hour. The hem is done. Let it go.""
$lines += ""
$lines += "Tessa looked down. The dress in her lap was finished -- deep blue wool for the miller's daughter, every stitch true. She had not noticed finishing. Her hands worked on their own when she was not watching."

# Quick write test first
Set-Content -Path $path -Value "" -Encoding utf8
$tempLines = $lines[0..20]
$tempLines | Set-Content -Path $path -Encoding utf8
Write-Output "Test write OK"

$wc = (Get-Content -Path $path -Raw).Length
Write-Output "File size: $wc"
Remove-Item $path -Force
