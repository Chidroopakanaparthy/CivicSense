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
  it('renders the main heading', () => {
    render(<Home />);
    expect(screen.getByText(/Empowering Your/i)).toBeInTheDocument();
    expect(screen.getByText(/Democratic/i)).toBeInTheDocument();
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
