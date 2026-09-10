<#
.SYNOPSIS
    网络配置工具：静默配置静态 IP 或恢复 DHCP（自动提权，无任何输出）
.DESCRIPTION
    默认操作适配器 AAAA；指定 -InterfaceAlias 可覆盖。
    所有输出（含错误）均被抑制，仅通过进程退出码反馈结果。
    退出码：0=成功，1=适配器不存在，2=配置失败
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("on", "off")]
    [string]$Action = "on",

    [Parameter(Mandatory = $false)]
    [string]$InterfaceAlias = "AAAA"
)

$ErrorActionPreference = 'SilentlyContinue'

# ========== 自动提权（隐藏窗口）==========
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    $psi = "-NoProfile -NoLogo -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`" -Action $Action -InterfaceAlias `"$InterfaceAlias`""
    $null = (New-Object -ComObject Shell.Application).ShellExecute("powershell.exe", $psi, "", "runas", 0)
    exit
}

# ========== 预设静态 IP 参数 ==========
$StaticIP      = "172.17.174.5"
$PrefixLength  = 16
$StaticGateway = "172.17.0.1"
$DnsPrimary    = "8.8.8.8"
$DnsSecondary  = "114.114.114.114"

# ========== 校验目标适配器 ==========
if (-NOT (Get-NetAdapter -Name $InterfaceAlias)) { exit 1 }

# ========== 执行操作 ==========
try {
    if ($Action -eq "on") {
        Remove-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Confirm:$false
        Remove-NetRoute     -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -Confirm:$false

        Set-NetIPInterface  -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Dhcp Disabled -ErrorAction Stop
        New-NetIPAddress    -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 `
                            -IPAddress $StaticIP -PrefixLength $PrefixLength `
                            -DefaultGateway $StaticGateway -ErrorAction Stop
        Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias `
                            -ServerAddresses "$DnsPrimary,$DnsSecondary" -ErrorAction Stop
    }
    else {
        Remove-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Confirm:$false
        Set-NetIPInterface  -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Dhcp Enabled -ErrorAction Stop
        Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ResetServerAddresses -ErrorAction Stop
        ipconfig /renew $InterfaceAlias | Out-Null
    }
    ipconfig /flushdns | Out-Null
}
catch {
    exit 2
}

exit 0