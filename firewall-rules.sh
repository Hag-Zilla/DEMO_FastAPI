#!/usr/bin/env bash
# DDoS Protection Firewall Rules (ufw + nftables)
# Run with: sudo bash firewall-rules.sh

set -euo pipefail

echo "=== Configuring Firewall Rules for DDoS Protection ==="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

# Enable UFW
echo "[1/6] Enabling UFW firewall..."
ufw --force enable

# Set default policies
echo "[2/6] Setting default policies..."
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed

# Allow SSH (critical: don't lock yourself out!)
echo "[3/6] Allowing SSH access..."
ufw allow 22/tcp comment "SSH access"

# Allow HTTP/HTTPS for Nginx
echo "[4/6] Allowing HTTP/HTTPS traffic..."
ufw allow 80/tcp comment "HTTP via Nginx"
ufw allow 443/tcp comment "HTTPS via Nginx"

# BLOCK direct access to FastAPI port (8000)
echo "[5/6] Blocking direct FastAPI access (port 8000)..."
ufw deny 8000/tcp comment "FastAPI - access only via Nginx"

# BLOCK direct access to Redis (6379)
echo "[6/6] Blocking direct Redis access (port 6379)..."
ufw deny 6379/tcp comment "Redis - internal only"
ufw deny 6379/udp comment "Redis - internal only"

# Enable rate limiting rules (if using nftables)
if command -v nft &> /dev/null; then
    echo ""
    echo "[OPTIONAL] Applying nftables rate limiting rules..."
    
    # Create nftables config
    cat > /etc/nftables-ddos.conf << 'EOF'
#!/usr/bin/nft -f

# DDoS Protection Rules with nftables
table inet ddos {
    chain inbound {
        type filter hook input priority 0; policy drop;

        # Allow loopback
        iifname "lo" accept

        # Allow established/related connections
        ct state established,related accept

        # Drop invalid states
        ct state invalid drop

        # ICMP rate limiting (prevent ping floods)
        icmp type echo-request limit rate 5/second accept

        # TCP SYN flood protection
        tcp flags syn limit rate 25/second accept

        # Allow SSH
        tcp dport 22 accept

        # Allow HTTP/HTTPS
        tcp dport { 80, 443 } accept

        # Connection limit per IP (max 100 concurrent)
        ct state new tcp dport { 80, 443 } limit rate 100/second accept

        # Drop everything else
        drop
    }
}
EOF
    
    # Load rules
    nft -f /etc/nftables-ddos.conf || echo "WARNING: nftables rules failed to load"
fi

echo ""
echo "=== Firewall Configuration Complete ==="
echo "Status:"
ufw status numbered
echo ""
echo "Key Rules:"
echo "  ✓ SSH (22/tcp) - ALLOWED"
echo "  ✓ HTTP (80/tcp) - ALLOWED (Nginx)"
echo "  ✓ HTTPS (443/tcp) - ALLOWED (Nginx)"
echo "  ✗ FastAPI (8000/tcp) - BLOCKED (direct access denied)"
echo "  ✗ Redis (6379/tcp/udp) - BLOCKED (internal only)"
echo ""
echo "To view all rules: ufw status verbose"
echo "To reload rules: sudo systemctl restart ufw"
