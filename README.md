# Line Item Automation Tool

A Flask web application for automating the creation of line items in Google Ad Manager (GAM) with support for currency exchange and price bucket targeting.

## Features

- **Automated Line Item Creation**: Create multiple line items in Google Ad Manager with custom targeting
- **Currency Exchange Support**: Convert prices between USD, INR, EUR, GBP, and JPY
- **Price Bucket Targeting**: Generate `pwtecp` values for precise price range targeting
- **Bidder Code Targeting**: Target specific demand partners using `pwtpid` values
- **Dynamic Network Code**: Switch between different Google Ad Manager networks without environment variable updates
- **Real-time Calculation**: Live calculation of line items and creatives with Google Ad Manager limit validation
- **Flexible Configuration**: Customize start/end prices, granularity, and currency settings
- **Web Interface**: User-friendly HTML form for easy configuration

## Prerequisites

- Python 3.7 or higher
- Google Ad Manager account with API access
- Google Ad Manager API credentials (`googleads.yaml`)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Lineitem-automation-tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Ad Manager credentials**:
   - Place your `googleads.yaml` file in the project root
   - Ensure the file contains your GAM network ID and API credentials

## Configuration

### Google Ad Manager Setup

1. Create a `googleads.yaml` file with your GAM credentials:
   ```yaml
   ad_manager:
     application_name: LineItemAutomationTool
     path_to_private_key_file: path/to/your/private-key.json
   ```

2. Update the network ID in `lineitem_flask_app/Openwrap_DFP_Setup/settings.py`:
   ```python
   DFP_NETWORK_CODE = 'your-network-id'
   ```

### Currency Settings

The application supports currency exchange with the following currencies:
- USD (default)
- INR (Indian Rupee)
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)

## Usage

1. **Start the Flask application**:
   ```bash
   cd lineitem_flask_app
   python app.py
   ```

2. **Access the web interface**:
   - Open your browser and go to `http://localhost:5000`
   - Fill in the form with your desired configuration

3. **Configure line items**:
   - **Start Price**: Beginning of the price range
   - **End Price**: End of the price range
   - **Granularity**: Price increment between line items (use -1 for catch-all buckets)
   - **Currency Code**: Base currency for calculations
   - **Currency Exchange**: Enable to convert prices to target currency
   - **Target Currency**: Currency to convert prices to (when exchange is enabled)
   - **Network Code**: Enter any Google Ad Manager network code (no environment variable updates needed)
   - **Bidder Name**: Optional bidder name for auto-generation of naming conventions
   - **Bidder Code**: Optional bidder code to target specific demand partners (e.g., pubmatic, appnexus, rubicon)
   - **Real-time Preview**: See calculated line items and creatives with limit validation

## How It Works

### Price Bucket Generation

The application generates price buckets based on your configuration:

```
Example: Start=5, End=7, Granularity=0.03
- Bucket 1: 5.00-5.02 (pwtecp: ["5.00", "5.01", "5.02"])
- Bucket 2: 5.03-5.05 (pwtecp: ["5.03", "5.04", "5.05"])
- ...
- Bucket 67: 6.98-6.99 (pwtecp: ["6.98", "6.99"])
```

### Currency Exchange

When currency exchange is enabled:
- **Price values** are converted to the target currency
- **pwtecp values** remain in USD (for bidding purposes)
- **Line item currency** is set to the target currency

### Line Item Creation

Each price bucket creates a line item with:
- Custom targeting using `pwtecp` values for price ranges
- Platform targeting using `pwtplt` values
- Bidder targeting using `pwtpid` values (when bidder code is specified)
- Clean, concise naming format: `HB $X.XX` (without "Top Bid" prefix)
- Appropriate currency settings
- Optimized for Google Ad Manager integration

### Real-time Calculation & Validation

The application provides live calculation and validation:

#### **Calculation Display**
- **Line Items**: Shows total number of line items that will be created
- **Creatives**: Shows total creatives (line items × creatives per line item)
- **Live Updates**: Calculations update as you modify ranges and settings

#### **Google Ad Manager Limits**
- **Line Items per Order**: Maximum 450 (enforced by Google)
- **Creatives per Advertiser**: Maximum 10,000 (enforced by Google)
- **Performance Warning**: Alert when exceeding 200 line items (recommended limit)

#### **Granularity Options**
- **Positive Values** (e.g., 0.01, 0.05, 0.10): Creates multiple line items with precise price increments
- **Catch-all (-1)**: Creates single line item targeting entire price range
- **Example**: Range 5.00-7.00 with 0.01 granularity = 200 line items

### Auto-Generation of Naming Conventions

When both **Bidder Name** and **Bidder Code** are provided, the application automatically generates:

#### **Auto-Generated Fields**
- **Order Name**: `Openwrap-{BIDDER_NAME}-Display1`
- **Advertiser Name**: `Network OpenWrap {BIDDER_NAME}`
- **Line Item Prefix**: `OpenWrap-{BIDDER_NAME}-display`

#### **Example Auto-Generation**
If you enter:
- **Bidder Name**: `PubMatic`
- **Bidder Code**: `pubmatic`

The system automatically populates:
- **Order Name**: `Openwrap-PubMatic-Display1`
- **Advertiser Name**: `Network OpenWrap PubMatic`
- **Line Item Prefix**: `OpenWrap-PubMatic-display`

#### **Benefits**
- **Consistent Naming**: Ensures standardized naming across all bidder setups
- **Time Saving**: No need to manually type repetitive naming patterns
- **Error Prevention**: Reduces typos and naming inconsistencies
- **Easy Management**: Makes it easier to identify and manage bidder-specific campaigns

## File Structure

```
Lineitem-automation-tool/
├── lineitem_flask_app/
│   ├── app.py                 # Main Flask application
│   ├── templates/
│   │   └── index.html        # Web interface
│   └── Openwrap_DFP_Setup/   # GAM integration modules
│       ├── settings.py       # Configuration settings
│       ├── dfp/
│       │   └── create_line_items.py
│       └── tasks/
│           └── dfp_utils.py
├── requirements.txt           # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## Security Notes

- **Never commit** your `googleads.yaml` file to version control
- **Keep API credentials** secure and private
- **Use environment variables** for sensitive configuration in production

## Troubleshooting

### Common Issues

1. **"INVALID_LINE_ITEM_CURRENCY" Error**:
   - Your GAM network may not support the selected currency
   - Use USD as the currency code or contact your GAM administrator

2. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **API Connection Issues**:
   - Verify your `googleads.yaml` configuration
   - Check network connectivity and API quotas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Google Ad Manager API documentation
- Create an issue in the GitHub repository 