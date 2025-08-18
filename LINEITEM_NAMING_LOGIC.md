# Line Item Naming Logic - Current Implementation

## Overview
After removing "Top Bid" from line item names, here's the complete naming logic for regular line items in the Google Ad Manager automation tool.

## 📋 **Current Naming Structure**

### **1. Regular Line Items (Granular Pricing)**
For line items with positive granularity (e.g., 0.01, 0.05, 0.10):

#### **With Line Item Prefix:**
```
Format: {lineitem_prefix}_HB ${price}
Example: OpenWrap-PubMatic-display_HB $5.00
```

#### **Without Line Item Prefix:**
```
Format: HB ${price}
Example: HB $5.00
```

### **2. Catch-All Line Items (Granularity = -1)**
For line items with granularity set to -1 (catch-all buckets):

#### **With Line Item Prefix:**
```
Format: {lineitem_prefix}_HB ${price}+ (Catch-all {start}-{end})
Example: OpenWrap-PubMatic-display_HB $15.00+ (Catch-all 15.0-20.0)
```

#### **Without Line Item Prefix:**
```
Format: HB ${price}+ (Catch-all {start}-{end})
Example: HB $15.00+ (Catch-all 15.0-20.0)
```

## 🎯 **Auto-Generated Prefix Logic**

When both **Bidder Name** and **Bidder Code** are provided, the system automatically generates:

```
Order Name = Openwrap-{BIDDER_NAME}-display
Line Item Prefix = OpenWrap-{BIDDER_NAME}-display
```

### **Examples:**
- **Bidder Name**: `PubMatic` → **Order Name**: `Openwrap-PubMatic-display`, **Prefix**: `OpenWrap-PubMatic-display`
- **Bidder Name**: `AppNexus` → **Order Name**: `Openwrap-AppNexus-display`, **Prefix**: `OpenWrap-AppNexus-display`
- **Bidder Name**: `Rubicon` → **Order Name**: `Openwrap-Rubicon-display`, **Prefix**: `OpenWrap-Rubicon-display`

## 📊 **Complete Examples**

### **Scenario 1: PubMatic Setup with Auto-Generated Prefix**
**Input:**
- Bidder Name: `PubMatic`
- Bidder Code: `pubmatic`
- Price Range: 5.00-7.00, Granularity: 0.01

**Generated Order Name:** `Openwrap-PubMatic-display`
**Generated Prefix:** `OpenWrap-PubMatic-display`

**Line Item Names:**
```
OpenWrap-PubMatic-display_HB $5.00
OpenWrap-PubMatic-display_HB $5.01
OpenWrap-PubMatic-display_HB $5.02
...
OpenWrap-PubMatic-display_HB $6.99
```

### **Scenario 2: AppNexus Setup with Catch-All**
**Input:**
- Bidder Name: `AppNexus`
- Bidder Code: `appnexus`
- Price Range: 10.00-20.00, Granularity: -1

**Generated Order Name:** `Openwrap-AppNexus-display`
**Generated Prefix:** `OpenWrap-AppNexus-display`

**Line Item Name:**
```
OpenWrap-AppNexus-display_HB $10.00+ (Catch-all 10.0-20.0)
```

### **Scenario 3: Generic Setup without Bidder Info**
**Input:**
- No Bidder Name or Code
- Price Range: 2.00-5.00, Granularity: 0.50

**Line Item Names:**
```
HB $2.00
HB $2.50
HB $3.00
HB $3.50
HB $4.00
HB $4.50
```

### **Scenario 4: Manual Prefix Override**
**Input:**
- Custom Line Item Prefix: `Custom-Header-Bidding`
- Price Range: 8.00-10.00, Granularity: 1.00

**Line Item Names:**
```
Custom-Header-Bidding_HB $8.00
Custom-Header-Bidding_HB $9.00
```

## 🔄 **Naming Decision Flow**

```
1. Check if Bidder Name AND Bidder Code are provided
   ├─ YES → Auto-generate prefix: "OpenWrap-{BIDDER_NAME}-display"
   └─ NO → Use manual prefix (if provided) or no prefix

2. Check granularity type
   ├─ Granularity = -1 → Catch-all format with "+" and range info
   └─ Granularity > 0 → Regular format with exact price

3. Apply naming template
   ├─ With Prefix → "{prefix}_HB ${price}[+ (Catch-all {start}-{end})]"
   └─ No Prefix → "HB ${price}[+ (Catch-all {start}-{end})]"
```

## 📈 **Real-World Naming Examples**

### **Standard Header Bidding Campaign**
```
Bidder: PubMatic
Ranges: 0.10-5.00 (0.01), 5.00-20.00 (0.10)

Generated Names:
OpenWrap-PubMatic-display_HB $0.10
OpenWrap-PubMatic-display_HB $0.11
...
OpenWrap-PubMatic-display_HB $4.99
OpenWrap-PubMatic-display_HB $5.00
OpenWrap-PubMatic-display_HB $5.10
...
OpenWrap-PubMatic-display_HB $19.90
```

### **Premium Inventory Setup**
```
Bidder: Rubicon
Ranges: 25.00-100.00 (-1)

Generated Name:
OpenWrap-Rubicon-display_HB $25.00+ (Catch-all 25.0-100.0)
```

### **Multi-Bidder Generic Setup**
```
No Bidder Info
Ranges: 1.00-10.00 (1.00)

Generated Names:
HB $1.00
HB $2.00
HB $3.00
...
HB $10.00
```

## ✨ **Key Benefits of Current Naming**

1. **Clean & Concise**: Removed verbose "Top Bid" text
2. **Clear Identification**: "HB" clearly indicates header bidding
3. **Bidder-Specific**: Auto-generated prefixes for easy organization
4. **Flexible**: Works with or without bidder information
5. **Scalable**: Consistent pattern for any number of price ranges
6. **Professional**: Modern programmatic advertising naming convention

## 🎯 **Character Count Comparison**

| Scenario | Old Format | New Format | Saved Characters |
|----------|------------|------------|------------------|
| With Prefix | `OpenWrap-PubMatic-display_Top Bid: HB $5.00` | `OpenWrap-PubMatic-display_HB $5.00` | 10 characters |
| Without Prefix | `Top Bid: HB $5.00` | `HB $5.00` | 10 characters |
| Catch-all | `OpenWrap-PubMatic-display_Top Bid: HB $15.00+ (Catch-all 15.0-20.0)` | `OpenWrap-PubMatic-display_HB $15.00+ (Catch-all 15.0-20.0)` | 10 characters |

**Result**: 10 characters saved per line item name, improving readability and reducing clutter in Google Ad Manager interface.