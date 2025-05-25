// frontend/app/api/slack/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  const body = await request.json();

  try {
    const response = await fetch(`${backendUrl}/api/v1/slack/send-message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const responseData = await response.json();
    
    if (!response.ok) {
      console.error('Backend Error:', responseData);
      return NextResponse.json(
        { error: responseData.detail || 'Backend request failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(responseData);
  } catch (error) {
    console.error('Proxy Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}