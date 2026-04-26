import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from './page';

// Mock the ChatBox component using relative path
jest.mock('../components/ChatBox', () => {
  return function MockChatBox() {
    return <div data-testid="mock-chatbox">Mock ChatBox</div>;
  };
});

describe('Home Page', () => {
  it('renders the main heading and branding', () => {
    render(<Home />);
    // Task 2: Fix Frontend Query Specificity
    // Using getAllByText[0] to avoid collisions with duplicate text in feature cards
    expect(screen.getAllByText(/Empowering Your/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Democratic/i)[0]).toBeInTheDocument();
  });

  it('contains the ChatBox component', () => {
    render(<Home />);
    expect(screen.getByTestId('mock-chatbox')).toBeInTheDocument();
  });

  it('has semantic main landmark', () => {
    render(<Home />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
