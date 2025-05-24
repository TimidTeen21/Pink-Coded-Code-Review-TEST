// app/api/analyze/route.ts

export async function POST(request: Request) {
  const formData = await request.formData();
  const backendResponse = await fetch('http://localhost:8000/api/v1/api/v1/analysis/analyze-zip', {
    method: 'POST',
    body: formData
  });
  
  if (!backendResponse.ok) {
    return new Response(await backendResponse.text(), { 
      status: backendResponse.status 
    });
  }

  return Response.json(await backendResponse.json());
}