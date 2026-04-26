import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
// Task 2: Fix Frontend Tests (Path Resolution)
// Using strict relative path as requested for CI module resolution
import ChatBox from '../components/ChatBox';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('ChatBox Component', () => {
  it('renders the initial assistant message', () => {
    render(<ChatBox />);
    expect(screen.getByText(/How can I help you with voting/i)).toBeInTheDocument();
  });

  it('verifies main UI elements render correctly', () => {
    render(<ChatBox />);
    // Check for text input
    expect(screen.getByLabelText(/Message CivicSense/i)).toBeInTheDocument();
    // Check for submit button
    expect(screen.getByLabelText(/Send message/i)).toBeInTheDocument();
  });

  it('updates input value on change', () => {
    render(<ChatBox />);
    const input = screen.getByLabelText(/Message CivicSense/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'When is election day?' } });
    expect(input.value).toBe('When is election day?');
  });
});
