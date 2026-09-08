<#
.SYNOPSIS
    网络配置工具：通过参数配置静态 IP 或恢复 DHCP（自动提权）
.DESCRIPTION
    自动检测网络适配器，根据 -Action 参数执行配置。
    默认操作为配置静态 IP（on），指定 off 则恢复 DHCP。
    可通过 -InterfaceAlias 指定适配器名称，否则自动选择第一个已连接的适配器。
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("on", "off")]
    [string]$Action = "on",

    [Parameter(Mandatory = $false)]
    [string]$InterfaceAlias = ""
)

# ========== 自动提权部分 ==========
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    Write-Host "当前不是管理员权限，正在请求提升..."
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action '$Action' -InterfaceAlias '$InterfaceAlias'" -Verb RunAs
    exit
}
Write-Host "现在拥有管理员权限"

# ========== 预设静态 IP 参数（可自行修改）==========
$StaticIP      = "172.17.174.5"
$PrefixLength  = 16          # 255.255.0.0
$StaticGateway = "172.17.0.1"
$DnsPrimary    = "8.8.8.8"
$DnsSecondary  = "114.114.114.114"

# ========== 确定目标适配器 ==========
if ([string]::IsNullOrWhiteSpace($InterfaceAlias)) {
    Write-Host "正在自动选择第一个已连接的适配器..." -ForegroundColor Cyan
    $adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Up" })
    if ($adapters.Count -eq 0) {
        Write-Host "未找到已连接的适配器，尝试使用所有可用适配器中的第一个。" -ForegroundColor Yellow
        $adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue)
    }
    if ($adapters.Count -eq 0) {
        Write-Host "错误：无法获取任何网络适配器。请检查系统或手动指定 -InterfaceAlias。" -ForegroundColor Red
        exit 1
    }
    $selectedAdapter = $adapters[0]
    $InterfaceAlias = $selectedAdapter.Name
    Write-Host "自动选择适配器: $InterfaceAlias" -ForegroundColor Green
} else {
    Write-Host "使用指定的适配器: $InterfaceAlias" -ForegroundColor Green
}

# ========== 执行操作 ==========
switch ($Action) {
    "on" {
        Write-Host "`n正在配置静态 IP..." -ForegroundColor Yellow
        try {
            # 清除现有配置
            Remove-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
            Remove-NetRoute -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -Confirm:$false -ErrorAction SilentlyContinue

            # 禁用 DHCP
            Set-NetIPInterface -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Dhcp Disabled -ErrorAction Stop

            # 配置静态 IP
            New-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 `
                -IPAddress $StaticIP -PrefixLength $PrefixLength -DefaultGateway $StaticGateway -ErrorAction Stop

            # 配置 DNS
            Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ServerAddresses "$DnsPrimary,$DnsSecondary" -ErrorAction Stop

            Write-Host "静态 IP 配置成功！" -ForegroundColor Green
            ipconfig /flushdns | Out-Null
        }
        catch {
            Write-Host "配置失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    "off" {
        Write-Host "`n正在恢复为自动获取 (DHCP)..." -ForegroundColor Yellow
        try {
            Remove-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
            Set-NetIPInterface -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Dhcp Enabled -ErrorAction Stop
            Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ResetServerAddresses -ErrorAction Stop
            Write-Host "已恢复为 DHCP！" -ForegroundColor Green
            Write-Host "正在重新获取 IP 地址..." -ForegroundColor Gray
            ipconfig /renew $InterfaceAlias | Out-Null
        }
        catch {
            Write-Host "配置失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# ========== 显示当前配置 ==========
Write-Host "`n当前网络配置：" -ForegroundColor Cyan
Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias | Format-List InterfaceAlias, IPv4Address, IPv4DefaultGateway, DnsServer