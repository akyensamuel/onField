#!/usr/bin/env python
"""
Test script to verify Sentry integration is working correctly.
Run this from the Django project directory:
    python test_sentry.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnFieldRecording.settings')
django.setup()

def test_sentry_configuration():
    """Test if Sentry is properly configured"""
    from django.conf import settings
    import sentry_sdk
    
    print("=" * 60)
    print("SENTRY CONFIGURATION TEST")
    print("=" * 60)
    
    # Check if DSN is configured
    sentry_dsn = getattr(settings, 'SENTRY_DSN', None)
    
    if not sentry_dsn:
        print("❌ SENTRY_DSN is not configured in settings")
        print("   Please add SENTRY_DSN to your .env file")
        return False
    
    print(f"✅ SENTRY_DSN is configured")
    print(f"   DSN: {sentry_dsn[:50]}...")  # Show partial DSN for security
    
    # Check if sentry_sdk is initialized
    client = sentry_sdk.Hub.current.client
    if client is None or client.dsn is None:
        print("❌ Sentry SDK is not initialized")
        return False
    
    print(f"✅ Sentry SDK is initialized")
    print(f"   Client DSN: {str(client.dsn)[:50]}...")
    print(f"   Environment: {client.options.get('environment', 'not set')}")
    print(f"   Sample Rate: {client.options.get('traces_sample_rate', 0)}")
    print(f"   Send PII: {client.options.get('send_default_pii', False)}")
    
    # Check integrations
    integrations = client.options.get('integrations', [])
    print(f"\n📦 Integrations loaded: {len(integrations)}")
    for integration in integrations:
        print(f"   - {integration.__class__.__name__}")
    
    return True


def test_sentry_capture():
    """Test if Sentry can capture events"""
    import sentry_sdk
    
    print("\n" + "=" * 60)
    print("TESTING SENTRY EVENT CAPTURE")
    print("=" * 60)
    
    try:
        # Capture a test message
        event_id = sentry_sdk.capture_message(
            "Test message from OnField Recording System",
            level="info"
        )
        
        if event_id:
            print(f"✅ Test message captured successfully")
            print(f"   Event ID: {event_id}")
            print(f"\n💡 Check your Sentry dashboard to see this event:")
            print(f"   https://sentry.io/organizations/[your-org]/issues/")
        else:
            print(f"⚠️  Message sent but no event ID returned")
            print(f"   This might happen if sampling is low or DSN is invalid")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to capture test message")
        print(f"   Error: {str(e)}")
        return False


def test_sentry_exception():
    """Test if Sentry can capture exceptions"""
    import sentry_sdk
    
    print("\n" + "=" * 60)
    print("TESTING SENTRY EXCEPTION CAPTURE")
    print("=" * 60)
    
    try:
        # Trigger a test exception
        raise ValueError("This is a test exception for Sentry monitoring")
        
    except ValueError as e:
        event_id = sentry_sdk.capture_exception(e)
        
        if event_id:
            print(f"✅ Test exception captured successfully")
            print(f"   Event ID: {event_id}")
            print(f"\n💡 Check your Sentry dashboard to see this exception:")
            print(f"   https://sentry.io/organizations/[your-org]/issues/")
        else:
            print(f"⚠️  Exception sent but no event ID returned")
        
        return True


def main():
    """Run all Sentry tests"""
    print("\n🔍 Starting Sentry Integration Tests...\n")
    
    # Test 1: Configuration
    config_ok = test_sentry_configuration()
    
    if not config_ok:
        print("\n❌ Sentry configuration test failed")
        print("   Please check your .env file and settings.py")
        return
    
    # Test 2: Message capture
    test_sentry_capture()
    
    # Test 3: Exception capture
    test_sentry_exception()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n📊 Next Steps:")
    print("   1. Log in to your Sentry dashboard")
    print("   2. Look for 2 new events (1 message + 1 exception)")
    print("   3. Verify environment is set correctly")
    print("   4. Check that Django integration is active")
    print("\n💡 If you don't see events, check:")
    print("   - DSN is correct in .env file")
    print("   - Sentry project exists and is active")
    print("   - Internet connection is working")
    print("   - No firewall blocking outbound requests")
    print("\n")


if __name__ == '__main__':
    main()
