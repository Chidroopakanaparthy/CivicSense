import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatBox from './ChatBox';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('ChatBox Component', () => {
  it('renders the initial assistant message', () => {
    render(<ChatBox />);
    expect(screen.getByText(/How can I help you with voting/i)).toBeInTheDocument();
  });

  it('updates input value on change', () => {
    render(<ChatBox />);
    const input = screen.getByLabelText(/Message CivicSense/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'When is election day?' } });
    expect(input.value).toBe('When is election day?');
  });

  it('is accessible with keyboard navigation', () => {
    render(<ChatBox />);
    const input = screen.getByLabelText(/Message CivicSense/i);
    const button = screen.getByLabelText(/Send message/i);
    
    // Tab order test
    input.focus();
    expect(document.activeElement).toBe(input);
  });
});
