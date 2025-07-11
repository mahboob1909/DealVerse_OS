/**
 * API utilities for DealVerse OS
 * Handles data export, API calls, and response processing
 */

export interface ExportOptions {
  includeHeaders?: boolean;
  includeSummary?: boolean;
  includeWatermark?: boolean;
  customBranding?: boolean;
}

export interface ExportRequest {
  data: any[];
  format: 'pdf' | 'excel' | 'csv' | 'powerpoint';
  filename: string;
  module: string;
  options: ExportOptions;
}

export interface ExportResponse {
  blob: Blob;
  filename: string;
  size: number;
}

/**
 * Export data in various formats
 */
export async function exportData(request: ExportRequest): Promise<ExportResponse> {
  const response = await fetch('/api/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  const contentDisposition = response.headers.get('Content-Disposition');
  const filename = contentDisposition
    ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
    : `${request.filename}.${getFileExtension(request.format)}`;

  return {
    blob,
    filename,
    size: blob.size,
  };
}

/**
 * Get file extension for format
 */
function getFileExtension(format: string): string {
  const extensions = {
    pdf: 'pdf',
    excel: 'xlsx',
    csv: 'csv',
    powerpoint: 'pptx',
  };
  return extensions[format as keyof typeof extensions] || 'pdf';
}

/**
 * Download blob as file
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Generic API request function
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Upload file to server
 */
export async function uploadFile(
  file: File,
  endpoint: string = '/upload'
): Promise<{ url: string; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`/api${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}
