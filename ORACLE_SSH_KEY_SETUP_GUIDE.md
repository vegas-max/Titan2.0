# 🔑 Oracle Cloud SSH Key Setup Guide

## ⚠️ IMPORTANT: SSH Keys Are For YOUR Use Only

**Your SSH keys should NEVER be added to this repository or shared publicly.**

This guide explains how to generate, configure, and use SSH keys to connect to YOUR Oracle Cloud Always Free tier instance.

---

## 📋 Table of Contents

- [Understanding SSH Keys](#understanding-ssh-keys)
- [Generating Your SSH Key Pair](#generating-your-ssh-key-pair)
- [Adding SSH Key to Oracle Cloud](#adding-ssh-key-to-oracle-cloud)
- [Connecting to Your Instance](#connecting-to-your-instance)
- [SSH Key Security Best Practices](#ssh-key-security-best-practices)
- [Troubleshooting SSH Connections](#troubleshooting-ssh-connections)

---

## 🔐 Understanding SSH Keys

### What Are SSH Keys?

SSH keys are a secure way to authenticate and connect to remote servers without using passwords. They consist of two parts:

1. **Private Key** (`id_rsa` or similar) - **KEEP THIS SECRET!**
   - Stays on YOUR local computer
   - Never share or upload this file
   - Acts like your password (but more secure)

2. **Public Key** (`id_rsa.pub` or similar) - Safe to share
   - Can be uploaded to servers you want to access
   - Uploaded to Oracle Cloud during instance creation
   - Cannot be used to access your account without the private key

### Why Use SSH Keys?

- ✅ More secure than passwords
- ✅ Cannot be brute-forced like passwords
- ✅ Required by Oracle Cloud for instance access
- ✅ Enables secure, automated deployments

---

## 🔨 Generating Your SSH Key Pair

### On Linux/macOS

Open a terminal and run:

```bash
# Generate a new SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# When prompted:
# - File location: Press Enter to accept default (~/.ssh/id_rsa)
# - Passphrase: Optional but recommended for extra security
```

**Example output:**
```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/username/.ssh/id_rsa): [Press Enter]
Enter passphrase (empty for no passphrase): [Type passphrase or press Enter]
Enter same passphrase again: [Type passphrase again or press Enter]
Your identification has been saved in /home/username/.ssh/id_rsa
Your public key has been saved in /home/username/.ssh/id_rsa.pub
```

### On Windows

**Option 1: Using Windows PowerShell**
```powershell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

**Option 2: Using PuTTYgen**
1. Download and install PuTTY: https://www.putty.org/
2. Open PuTTYgen
3. Click "Generate" and move mouse randomly
4. Save private key as `id_rsa.ppk`
5. Copy public key text for Oracle Cloud

### Verify Your Keys Were Created

```bash
# List your SSH keys
ls -la ~/.ssh/

# You should see:
# id_rsa       (private key - KEEP SECRET)
# id_rsa.pub   (public key - safe to upload)
```

---

## ☁️ Adding SSH Key to Oracle Cloud

### During Instance Creation

1. **Login to Oracle Cloud Console**
   - Navigate to: https://cloud.oracle.com/

2. **Create New Instance**
   - Go to: **Compute** → **Instances** → **Create Instance**

3. **Configure SSH Keys Section**
   - Scroll to "Add SSH keys" section
   - Choose one of these options:

#### Option A: Upload Public Key File (Recommended)

```bash
# First, view your public key to verify it's correct
cat ~/.ssh/id_rsa.pub
```

- Click "Upload public key files (.pub)"
- Select your `id_rsa.pub` file
- Click "Upload"

#### Option B: Paste Public Key Contents

```bash
# Copy your public key to clipboard
# On Linux/macOS:
cat ~/.ssh/id_rsa.pub | pbcopy  # macOS
cat ~/.ssh/id_rsa.pub | xclip -selection clipboard  # Linux

# On Windows (PowerShell):
Get-Content ~/.ssh/id_rsa.pub | Set-Clipboard
```

- Click "Paste public keys"
- Paste your public key contents
- Should start with: `ssh-rsa AAAAB3NzaC1yc2E...`

**Example public key format:**
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCvSjSye0XFzwqtL6zpwLigkSs8NOXotl9wWsfLdQdFctlZjd4clJ1CpLwGFEhoUunDAt8CfLRrnyEcemmOi2dl1qVxfPFaKY7kktIMqHxvOqkE9wlB6QcmfnwjmTcXVOkiVXovYEWiOqUYdfDrj+43bBO/GvhDbKrRZcReKprrB9JFkdFkumtwC2pJ7mGYxWvYTDb6cTxnTzntqrQ9kdI7c0I2vlypupVL+5Wg0XVInd5jI6pMDgq+kpJhlB0OMTJotnVu4w7DzL82AbrUrweJiquW3zliV9SV6o4fH62JCVP49g7IT5iL/0Xvuq+ECgWiHxTsFGb3A2LAsNwyTW9z your_email@example.com
```

4. **Complete Instance Creation**
   - Configure other settings (name, shape, network, etc.)
   - Click "Create"
   - Wait for instance to provision (2-3 minutes)

### After Instance Creation

If you forgot to add your SSH key during creation, you can add it later:

1. **Access Instance Console**
   - Go to instance details
   - Click "Console Connection"
   - Use web-based console to login
   
2. **Add Key Manually**
   ```bash
   # Add your public key to authorized_keys
   echo "ssh-rsa AAAAB3Nza..." >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

---

## 🔌 Connecting to Your Instance

### Basic SSH Connection

Once your Oracle Cloud instance is running:

```bash
# Replace YOUR_PUBLIC_IP with your instance's public IP address
ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP

# For Ubuntu instances:
ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP

# If you used a different key name:
ssh -i ~/.ssh/my_custom_key opc@YOUR_PUBLIC_IP
```

### First Connection

On your first connection, you'll see:

```
The authenticity of host 'YOUR_PUBLIC_IP' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

Type `yes` and press Enter.

### Create SSH Config for Easy Access (Optional)

Create/edit `~/.ssh/config`:

```bash
# Edit SSH config
nano ~/.ssh/config

# Add this configuration:
Host titan-oracle
    HostName YOUR_PUBLIC_IP
    User opc
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Now you can connect easily:
```bash
ssh titan-oracle
```

### Using PuTTY (Windows)

1. **Open PuTTY**

2. **Configure Connection:**
   - Host Name: `opc@YOUR_PUBLIC_IP`
   - Port: 22
   - Connection type: SSH

3. **Add Private Key:**
   - Left panel: Connection → SSH → Auth
   - Browse and select your `.ppk` private key file

4. **Save Session:**
   - Left panel: Session
   - Saved Sessions: Enter name (e.g., "Titan Oracle")
   - Click "Save"

5. **Connect:**
   - Click "Open"

---

## 🔒 SSH Key Security Best Practices

### DO's ✅

1. **Protect Your Private Key**
   ```bash
   # Set correct permissions
   chmod 600 ~/.ssh/id_rsa
   chmod 644 ~/.ssh/id_rsa.pub
   ```

2. **Use a Passphrase**
   - Adds extra layer of security
   - Required even if private key is stolen

3. **Backup Your Keys**
   ```bash
   # Backup to secure location (encrypted USB drive, password manager, etc.)
   cp ~/.ssh/id_rsa* /path/to/secure/backup/
   ```

4. **Use Different Keys for Different Purposes**
   - Consider separate keys for different servers
   - Makes revocation easier if one is compromised

5. **Keep Keys in .gitignore**
   - Repository already excludes `.env` files
   - NEVER commit SSH keys to git

### DON'Ts ❌

1. **NEVER Share Your Private Key**
   - Not via email, chat, or any other method
   - Not even with "trusted" people or services

2. **NEVER Commit Keys to Git**
   ```bash
   # ❌ WRONG - Don't do this!
   git add ~/.ssh/id_rsa
   
   # ❌ WRONG - Don't add to repository
   cp ~/.ssh/id_rsa /path/to/Titan2.0/
   ```

3. **NEVER Store Keys in Cloud Storage Unencrypted**
   - Don't put in Dropbox, Google Drive, etc. without encryption

4. **NEVER Use Default Passwords**
   - Oracle instances require SSH keys (good!)
   - Don't enable password authentication

5. **NEVER Ignore Permission Warnings**
   ```bash
   # If you see this error, fix permissions:
   # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
   # @ WARNING: UNPROTECTED PRIVATE KEY FILE! @
   # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
   
   chmod 600 ~/.ssh/id_rsa
   ```

---

## 🔧 Troubleshooting SSH Connections

### Problem: Permission Denied (publickey)

**Symptoms:**
```
Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

**Solutions:**

1. **Verify you're using the correct username**
   ```bash
   # Oracle Linux/CentOS:
   ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
   
   # Ubuntu:
   ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP
   ```

2. **Verify correct key is being used**
   ```bash
   ssh -i ~/.ssh/id_rsa -v opc@YOUR_PUBLIC_IP
   # The -v flag shows debug info
   ```

3. **Check key permissions**
   ```bash
   ls -la ~/.ssh/id_rsa
   # Should show: -rw------- (600)
   
   chmod 600 ~/.ssh/id_rsa
   ```

4. **Verify public key is on server**
   - Login via Console Connection
   - Check: `cat ~/.ssh/authorized_keys`

### Problem: Connection Timeout

**Symptoms:**
```
ssh: connect to host YOUR_PUBLIC_IP port 22: Connection timed out
```

**Solutions:**

1. **Check Security List (Firewall) Rules**
   - Oracle Cloud Console → Networking → VCN → Security Lists
   - Ensure Ingress Rule for Port 22 exists
   - Source CIDR: `0.0.0.0/0` or your IP

2. **Check Instance Firewall**
   ```bash
   # After logging in via Console:
   
   # Oracle Linux:
   sudo firewall-cmd --list-all
   sudo firewall-cmd --permanent --add-port=22/tcp
   sudo firewall-cmd --reload
   
   # Ubuntu:
   sudo ufw status
   sudo ufw allow 22/tcp
   ```

3. **Verify Instance is Running**
   - Check instance state in Oracle Cloud Console
   - Should show: "Running" (green)

### Problem: Host Key Verification Failed

**Symptoms:**
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED! @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

**Solution:**

This happens when you recreate an instance with the same IP.

```bash
# Remove old host key
ssh-keygen -R YOUR_PUBLIC_IP

# Or edit and manually remove the line:
nano ~/.ssh/known_hosts
```

### Problem: Too Many Authentication Failures

**Symptoms:**
```
Received disconnect from YOUR_PUBLIC_IP: 2: Too many authentication failures
```

**Solution:**

```bash
# Specify which key to use explicitly
ssh -o IdentitiesOnly=yes -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
```

---

## 📝 Quick Reference

### Commands

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# View public key (safe to share)
cat ~/.ssh/id_rsa.pub

# Set correct permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Connect to Oracle Cloud instance
ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP

# Connect with verbose output (debugging)
ssh -i ~/.ssh/id_rsa -v opc@YOUR_PUBLIC_IP

# Copy file to instance
scp -i ~/.ssh/id_rsa file.txt opc@YOUR_PUBLIC_IP:~/

# Copy file from instance
scp -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP:~/file.txt ./
```

### File Locations

```
~/.ssh/id_rsa          # Private key (KEEP SECRET)
~/.ssh/id_rsa.pub      # Public key (upload to Oracle Cloud)
~/.ssh/config          # SSH client configuration (optional)
~/.ssh/known_hosts     # Known host fingerprints
~/.ssh/authorized_keys # On server: authorized public keys
```

---

## 🎯 What To Do vs What NOT To Do

### ✅ DO THIS: Correct SSH Key Workflow

1. **Generate SSH key pair on YOUR computer**
   ```bash
   ssh-keygen -t rsa -b 4096
   ```

2. **Upload PUBLIC key to Oracle Cloud**
   - During instance creation
   - Or add to `~/.ssh/authorized_keys` later

3. **Keep PRIVATE key on YOUR computer only**
   - Never upload anywhere
   - Never share with anyone

4. **Connect using YOUR private key**
   ```bash
   ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
   ```

### ❌ DON'T DO THIS: Common Mistakes

1. **DON'T add SSH keys to Titan repository**
   ```bash
   # ❌ WRONG
   cp ~/.ssh/id_rsa /path/to/Titan2.0/config/
   git add config/id_rsa
   ```

2. **DON'T share private key in issues or chat**
   ```bash
   # ❌ WRONG
   "Here's my private key: ssh-rsa AAAA..."
   ```

3. **DON'T upload private key to Oracle Cloud**
   - Only upload PUBLIC key (id_rsa.pub)

4. **DON'T email or message keys**
   - Not even encrypted

---

## 📞 Need Help?

If you're still having SSH connection issues:

1. **Check Oracle Cloud Console**
   - Verify instance is running
   - Check public IP is correct
   - Verify security rules allow port 22

2. **Use Console Connection**
   - Oracle Cloud Console → Instance Details → Console Connection
   - Provides browser-based access even if SSH fails

3. **Review Oracle Documentation**
   - https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/accessinginstance.htm

4. **Check Titan Documentation**
   - [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md)
   - [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
   - [ORACLE_QUICKSTART.md](ORACLE_QUICKSTART.md)

---

## 🔑 Summary

**Remember:**
- ✅ SSH keys are for YOUR use to connect to YOUR Oracle Cloud instance
- ✅ Generate keys on YOUR local computer
- ✅ Upload ONLY the PUBLIC key (.pub) to Oracle Cloud
- ✅ NEVER share or commit your PRIVATE key
- ✅ Keep private key permissions set to 600
- ✅ Use SSH keys to deploy Titan to your instance

**Your SSH keys should NEVER appear in the Titan2.0 repository!**

---

**For deployment instructions, see:** [ORACLE_QUICKSTART.md](ORACLE_QUICKSTART.md)
