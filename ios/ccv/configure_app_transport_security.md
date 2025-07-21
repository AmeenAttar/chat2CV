# Configure App Transport Security in Xcode

Since we removed the manual Info.plist file, you need to configure App Transport Security settings directly in Xcode:

## Steps:

1. **Open your Xcode project** (`ios/ccv/ccv.xcodeproj`)

2. **Select the project** in the navigator (the blue project icon at the top)

3. **Select the "ccv" target** (not the project, but the target underneath it)

4. **Go to the "Info" tab**

5. **Add App Transport Security settings:**
   - Click the "+" button next to "Custom iOS Target Properties"
   - Add a new key: `App Transport Security Settings` (type: Dictionary)
   - Under this dictionary, add:
     - `Allow Arbitrary Loads` (type: Boolean) = `NO`
     - `Exception Domains` (type: Dictionary)
       - Under Exception Domains, add `localhost` (type: Dictionary)
         - `NSExceptionAllowsInsecureHTTPLoads` (type: Boolean) = `YES`
         - `NSExceptionMinimumTLSVersion` (type: String) = `TLSv1.0`
         - `NSExceptionRequiresForwardSecrecy` (type: Boolean) = `NO`

## Alternative: Quick Configuration

If you prefer, you can also add this to your project's Info.plist by:

1. Right-click on your project in Xcode
2. "Add Files to 'ccv'"
3. Create a new "Property List" file named "Info"
4. Add the App Transport Security settings as described above

## What this does:

This configuration allows your app to make HTTP requests to `localhost` (your backend) while maintaining security for all other connections. 