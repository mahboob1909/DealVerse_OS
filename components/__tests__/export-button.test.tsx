import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExportButton, ExportOption } from '../ui/export-button';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => 'mock-token'),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  },
});

// Mock URL.createObjectURL
Object.defineProperty(window, 'URL', {
  value: {
    createObjectURL: jest.fn(() => 'mock-url'),
    revokeObjectURL: jest.fn(),
  },
});

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ExportButton Component', () => {
  const mockOptions: ExportOption[] = [
    {
      label: 'Export as PDF',
      format: 'pdf',
      icon: null,
      endpoint: '/api/export/pdf',
      filename: 'test-export.pdf',
    },
    {
      label: 'Export as Excel',
      format: 'excel',
      icon: null,
      endpoint: '/api/export/excel',
      filename: 'test-export.xlsx',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });

  it('renders single export button correctly', () => {
    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    expect(exportButton).toBeInTheDocument();
  });

  it('renders dropdown for multiple options', () => {
    render(<ExportButton options={mockOptions} />);

    const exportButton = screen.getByRole('button', { name: /export/i });
    expect(exportButton).toBeInTheDocument();
  });

  it('opens dropdown when clicked with multiple options', async () => {
    const user = userEvent.setup();
    render(<ExportButton options={mockOptions} />);

    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    expect(screen.getByText('Export as PDF')).toBeInTheDocument();
    expect(screen.getByText('Export as Excel')).toBeInTheDocument();
  });

  it('handles PDF export correctly', async () => {
    const user = userEvent.setup();
    const mockBlob = new Blob(['mock pdf content'], { type: 'application/pdf' });

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
    });

    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/export/pdf', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
        },
      });
    });
  });

  it('handles Excel export correctly', async () => {
    const user = userEvent.setup();
    const mockBlob = new Blob(['mock excel content'], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
    });

    render(<ExportButton options={mockOptions} />);

    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    const excelOption = screen.getByText('Export as Excel');
    await user.click(excelOption);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/export/excel', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
        },
      });
    });
  });

  it('shows loading state during export', async () => {
    const user = userEvent.setup();

    // Mock a slow response
    (fetch as jest.Mock).mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        blob: () => Promise.resolve(new Blob(['content'])),
      }), 1000))
    );

    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    await user.click(exportButton);

    // Check for loading spinner
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('handles export errors gracefully', async () => {
    const user = userEvent.setup();
    const { toast } = require('sonner');

    (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to export export as pdf');
    });
  });

  it('handles successful export with toast notification', async () => {
    const user = userEvent.setup();
    const { toast } = require('sonner');
    const mockBlob = new Blob(['mock content']);

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
    });

    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Export as PDF exported successfully');
    });
  });

  it('handles disabled state correctly', () => {
    render(<ExportButton options={mockOptions} disabled={true} />);

    const exportButton = screen.getByRole('button', { name: /export/i });
    expect(exportButton).toBeDisabled();
  });

  it('uses resource ID in endpoint when provided', async () => {
    const user = userEvent.setup();
    const mockBlob = new Blob(['mock content']);

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
    });

    const optionWithId: ExportOption[] = [{
      label: 'Export Report',
      format: 'pdf',
      icon: null,
      endpoint: '/api/reports/{id}/export',
      filename: 'report.pdf',
    }];

    render(<ExportButton options={optionWithId} resourceId="123" />);

    const exportButton = screen.getByRole('button', { name: /export report/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/reports/123/export', expect.any(Object));
    });
  });

  it('creates download link correctly', async () => {
    const user = userEvent.setup();
    const mockBlob = new Blob(['mock content']);
    const mockCreateObjectURL = jest.fn(() => 'mock-url');
    const mockRevokeObjectURL = jest.fn();

    Object.defineProperty(window, 'URL', {
      value: {
        createObjectURL: mockCreateObjectURL,
        revokeObjectURL: mockRevokeObjectURL,
      },
    });

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
    });

    const singleOption = [mockOptions[0]];
    render(<ExportButton options={singleOption} />);

    const exportButton = screen.getByRole('button', { name: /export as pdf/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('mock-url');
    });
  });
});
