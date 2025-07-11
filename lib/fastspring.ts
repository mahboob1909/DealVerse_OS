/**
 * FastSpring integration utilities for DealVerse OS
 */

// FastSpring Store Builder Library types
declare global {
  interface Window {
    fastspring: {
      configure: (config: FastSpringConfig) => void;
      popup: (options: FastSpringPopupOptions) => void;
      builder: {
        push: (config: any) => void;
      };
    };
  }
}

interface FastSpringConfig {
  storefront: string;
  apiKey?: string;
  language?: string;
  country?: string;
  currency?: string;
}

interface FastSpringPopupOptions {
  path: string;
  email?: string;
  coupon?: string;
  tags?: string[];
  paymentMethod?: string;
  onSuccess?: (order: any) => void;
  onError?: (error: any) => void;
  onClose?: () => void;
}

interface FastSpringProduct {
  path: string;
  name: string;
  price: number;
  currency: string;
  billingCycle: 'monthly' | 'annual';
  description: string;
}

// FastSpring configuration
const FASTSPRING_CONFIG = {
  // TODO: Replace with your actual FastSpring store ID
  storefront: process.env.NEXT_PUBLIC_FASTSPRING_STORE_ID || 'dealverse.fspring.com',
  language: 'en',
  country: 'US',
  currency: 'USD'
};

// Product definitions matching our pricing
export const FASTSPRING_PRODUCTS: Record<string, FastSpringProduct> = {
  'professional-monthly': {
    path: 'dealverse-professional-monthly',
    name: 'DealVerse OS Professional',
    price: 25.00,
    currency: 'USD',
    billingCycle: 'monthly',
    description: 'AI-powered investment banking platform - Professional plan'
  },
  'professional-annual': {
    path: 'dealverse-professional-annual',
    name: 'DealVerse OS Professional Annual',
    price: 20.00, // Monthly equivalent
    currency: 'USD',
    billingCycle: 'annual',
    description: 'AI-powered investment banking platform - Annual plan (Save 20%)'
  },
  'enterprise': {
    path: 'dealverse-enterprise',
    name: 'DealVerse OS Enterprise',
    price: 0, // Custom pricing
    currency: 'USD',
    billingCycle: 'annual',
    description: 'Enterprise-grade investment banking platform with custom features'
  }
};

/**
 * Initialize FastSpring Store Builder Library
 */
export function initializeFastSpring(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Check if FastSpring is already loaded
    if (window.fastspring) {
      window.fastspring.configure(FASTSPRING_CONFIG);
      resolve();
      return;
    }

    // Load FastSpring SBL script
    const script = document.createElement('script');
    script.src = 'https://d1f8f0ekxec3v3.cloudfront.net/sbl/0.9.2/fastspring.min.js';
    script.async = true;
    
    script.onload = () => {
      if (window.fastspring) {
        window.fastspring.configure(FASTSPRING_CONFIG);
        resolve();
      } else {
        reject(new Error('FastSpring failed to load'));
      }
    };
    
    script.onerror = () => {
      reject(new Error('Failed to load FastSpring script'));
    };
    
    document.head.appendChild(script);
  });
}

/**
 * Open FastSpring checkout popup for a specific product
 */
export async function openCheckout(
  productKey: keyof typeof FASTSPRING_PRODUCTS,
  userEmail?: string,
  options?: Partial<FastSpringPopupOptions>
): Promise<void> {
  try {
    // Ensure FastSpring is initialized
    await initializeFastSpring();
    
    const product = FASTSPRING_PRODUCTS[productKey];
    if (!product) {
      throw new Error(`Product not found: ${productKey}`);
    }

    const popupOptions: FastSpringPopupOptions = {
      path: product.path,
      email: userEmail,
      onSuccess: (order) => {
        console.log('FastSpring order completed:', order);
        // Handle successful payment
        handlePaymentSuccess(order);
        options?.onSuccess?.(order);
      },
      onError: (error) => {
        console.error('FastSpring payment error:', error);
        // Handle payment error
        handlePaymentError(error);
        options?.onError?.(error);
      },
      onClose: () => {
        console.log('FastSpring popup closed');
        options?.onClose?.();
      },
      ...options
    };

    window.fastspring.popup(popupOptions);
  } catch (error) {
    console.error('Failed to open FastSpring checkout:', error);
    throw error;
  }
}

/**
 * Handle successful payment
 */
function handlePaymentSuccess(order: any) {
  // Redirect to dashboard or show success message
  if (typeof window !== 'undefined') {
    // You can add custom success handling here
    // For example, redirect to dashboard or show a success toast
    window.location.href = '/dashboard?payment=success';
  }
}

/**
 * Handle payment error
 */
function handlePaymentError(error: any) {
  // Show error message to user
  console.error('Payment failed:', error);
  // You can add custom error handling here
  // For example, show an error toast or modal
}

/**
 * Get product information by key
 */
export function getProduct(productKey: keyof typeof FASTSPRING_PRODUCTS): FastSpringProduct | null {
  return FASTSPRING_PRODUCTS[productKey] || null;
}

/**
 * Get all available products
 */
export function getAllProducts(): FastSpringProduct[] {
  return Object.values(FASTSPRING_PRODUCTS);
}

/**
 * Format price for display
 */
export function formatPrice(price: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(price);
}

/**
 * Calculate annual savings
 */
export function calculateAnnualSavings(): { monthlyTotal: number; annualTotal: number; savings: number; savingsPercent: number } {
  const monthly = FASTSPRING_PRODUCTS['professional-monthly'];
  const annual = FASTSPRING_PRODUCTS['professional-annual'];
  
  const monthlyTotal = monthly.price * 12;
  const annualTotal = annual.price * 12;
  const savings = monthlyTotal - annualTotal;
  const savingsPercent = Math.round((savings / monthlyTotal) * 100);
  
  return {
    monthlyTotal,
    annualTotal,
    savings,
    savingsPercent
  };
}

/**
 * Check if FastSpring is available
 */
export function isFastSpringAvailable(): boolean {
  return typeof window !== 'undefined' && !!window.fastspring;
}

/**
 * Preload FastSpring for better performance
 */
export function preloadFastSpring(): void {
  if (typeof window !== 'undefined' && !window.fastspring) {
    initializeFastSpring().catch(console.error);
  }
}
