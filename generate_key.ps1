[byte[]]$bytes = New-Object byte[] 32
(New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
[System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()