# Dynamic Network Code Configuration Guide

## Overview
The Line Item Automation Tool now supports dynamic network code configuration, allowing you to work with different Google Ad Manager networks without updating environment variables each time.

## 🎯 **How It Works**

### **Form-Based Network Code**
- Enter any network code directly in the web form
- The application dynamically configures the Google Ad Manager client
- No need to update Render.com environment variables for each network change

### **Fallback System**
The application uses a priority system for network code configuration:

1. **Form Input** (Highest Priority): Network code entered in the web form
2. **Environment Variable**: `NETWORK_CODE` environment variable (if set)
3. **Default Fallback**: `15671365` (if no other source available)

## 🔧 **Configuration Options**

### **Option 1: Dynamic Form Input (Recommended)**
Simply enter the network code in the web form:
```
Network Code: [123456789]
```
✅ **Benefits:**
- No environment variable updates needed
- Switch between networks instantly
- Perfect for agencies managing multiple clients

### **Option 2: Environment Variable (Optional)**
Set a default network code in Render.com environment variables:
```
NETWORK_CODE=123456789
```
✅ **Benefits:**
- Pre-fills the form with your most common network
- Still allows form override when needed

### **Option 3: Hardcoded Default**
If no form input or environment variable is provided, uses `15671365`

## 📋 **Usage Examples**

### **Single Network Setup**
If you always use the same network:
1. Set `NETWORK_CODE=123456789` in Render.com environment variables
2. The form will pre-fill with this value
3. You can still override it in the form if needed

### **Multi-Network Agency Setup**
If you manage multiple client networks:
1. Don't set any environment variable
2. Enter the appropriate network code for each campaign in the form
3. Switch between networks without any configuration changes

### **Client-Specific Campaigns**
```
Client A: Network Code 111111111
Client B: Network Code 222222222
Client C: Network Code 333333333
```
Just enter the appropriate code in the form for each client!

## 🔄 **Migration Guide**

### **Current Setup (Before)**
- Network code hardcoded in environment variables
- Required Render.com environment update for each network change
- Limited to single network per deployment

### **New Setup (After)**
- Network code entered in web form
- Optional environment variable for default value
- Support for unlimited networks per deployment

### **Migration Steps**
1. **No Action Required**: Existing setup continues to work
2. **Optional**: Set `NETWORK_CODE` environment variable for your default network
3. **Benefit**: Can now use any network code via the form

## 🎯 **Technical Implementation**

### **Dynamic Configuration Flow**
```
1. User enters network code in form
2. Flask app receives network_code parameter
3. Application calls setup_googleads_for_render(network_code)
4. Google Ads YAML file is regenerated with new network code
5. All API calls use the new network configuration
```

### **Code Changes**
```python
# Before (Static)
yaml_content = f"""ad_manager:
  application_name: API-Access
  network_code: '15671365'  # Hardcoded
  path_to_private_key_file: {json_path}"""

# After (Dynamic)
network_code = form_network_code or os.environ.get('NETWORK_CODE', '15671365')
yaml_content = f"""ad_manager:
  application_name: API-Access
  network_code: '{network_code}'  # Dynamic
  path_to_private_key_file: {json_path}"""
```

## 📊 **Comparison Table**

| Feature | Old Method | New Method |
|---------|------------|------------|
| Network Changes | Update environment variables | Enter in form |
| Deployment Required | Yes | No |
| Multi-Network Support | Limited | Unlimited |
| Setup Complexity | High | Low |
| Client Switching | Manual deployment | Instant |
| Environment Variables | Required for each network | Optional default only |

## 🚀 **Benefits**

### **For Agencies**
- ✅ Manage multiple client networks from single deployment
- ✅ No technical setup required for new clients
- ✅ Instant network switching
- ✅ Reduced operational overhead

### **For Publishers**
- ✅ Easy network code changes
- ✅ No environment variable management
- ✅ Form-based configuration
- ✅ Immediate effect

### **For Developers**
- ✅ Cleaner architecture
- ✅ Reduced configuration complexity
- ✅ Better user experience
- ✅ More flexible deployment

## 🔒 **Security Considerations**

- Network codes are not sensitive information (they're visible in GAM URLs)
- Form input is validated and sanitized
- Environment variables remain secure
- No additional security risks introduced

## 🎉 **Getting Started**

### **Immediate Use**
1. Open the line item creation form
2. Enter your network code in the "Network Code" field
3. Fill out the rest of the form normally
4. Submit - the application will use your specified network code

### **Set Default (Optional)**
1. Go to Render.com dashboard
2. Add environment variable: `NETWORK_CODE=your_default_code`
3. Redeploy (one-time setup)
4. Form will now pre-fill with your default network code

## 💡 **Pro Tips**

1. **Bookmark Different URLs**: You can bookmark the form with different network codes pre-filled
2. **Client Templates**: Create documentation templates with network codes for each client
3. **Testing**: Use test network codes for development without affecting production
4. **Validation**: The application will validate network codes with Google Ad Manager API

This enhancement makes the tool much more flexible and user-friendly for agencies and publishers managing multiple Google Ad Manager networks!