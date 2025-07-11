import React from 'react';
import { render, screen } from '@testing-library/react';
import { RecentDeals } from '@/components/dashboard/recent-deals';

const mockDeals = [
  {
    id: '1',
    clientName: 'Acme Corp',
    projectTitle: 'Website Redesign',
    status: 'negotiation' as const,
    avatarUrl: '/avatars/01.png',
    fallbackInitials: 'AC',
    createdAt: new Date('2024-01-15'),
    value: 15000,
  },
  {
    id: '2',
    clientName: 'TechTron Inc.',
    projectTitle: 'Mobile App Development',
    status: 'proposal' as const,
    avatarUrl: '/avatars/02.png',
    fallbackInitials: 'TT',
    createdAt: new Date('2024-01-10'),
    value: 25000,
  },
];

describe('RecentDeals Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders deals correctly', () => {
      render(<RecentDeals deals={mockDeals} useHook={false} />);

      expect(screen.getByText('Acme Corp')).toBeInTheDocument();
      expect(screen.getByText('Website Redesign')).toBeInTheDocument();
      expect(screen.getByText('TechTron Inc.')).toBeInTheDocument();
      expect(screen.getByText('Mobile App Development')).toBeInTheDocument();
    });

    it('displays deal values correctly', () => {
      render(<RecentDeals deals={mockDeals} useHook={false} />);

      expect(screen.getByText('$15,000')).toBeInTheDocument();
      expect(screen.getByText('$25,000')).toBeInTheDocument();
    });

    it('displays status badges correctly', () => {
      render(<RecentDeals deals={mockDeals} useHook={false} />);

      expect(screen.getByText('Negotiation')).toBeInTheDocument();
      expect(screen.getByText('Proposal')).toBeInTheDocument();
    });

    it('displays avatar fallbacks when no image', () => {
      render(<RecentDeals deals={mockDeals} useHook={false} />);

      expect(screen.getByText('AC')).toBeInTheDocument();
      expect(screen.getByText('TT')).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('shows skeleton loader when loading', () => {
      render(<RecentDeals isLoading={true} useHook={false} />);

      // Check for skeleton elements (they should have animate-pulse class)
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Empty States', () => {
    it('shows empty message when no deals', () => {
      render(<RecentDeals deals={[]} useHook={false} />);

      expect(screen.getByText('No recent deals found.')).toBeInTheDocument();
    });
  });
});
