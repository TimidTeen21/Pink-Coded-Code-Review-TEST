// frontend/troubleshoot.ts
/*To run the script, use the following command:
1. cd into the frontend directory
2. Use the command: node --loader ts-node/esm troubleshoot.ts
*/

import axios from 'axios';
import { execSync } from 'child_process';

// Test configuration
const config = {
  frontendUrl: 'http://localhost:3000',
  backendUrl: 'http://localhost:8000',
  testUser: {
    email: 'test@example.com',
    password: 'testpassword123'
  }
};

// Test cases
const tests = {
  dockerServices: {
    description: 'Check if Docker services are running',
    test: () => {
      try {
        const output = execSync('docker-compose ps').toString();
        const services = ['frontend', 'backend'];
        const missing = services.filter(s => !output.includes(s));
        if (missing.length > 0) {
          throw new Error(`Missing services: ${missing.join(', ')}`);
        }
        return true;
      } catch (error) {
        if (error instanceof Error) {
          throw new Error(`Docker services check failed: ${error.message}`);
        } else {
          throw new Error('Docker services check failed: Unknown error');
        }
      }
    }
  },
  frontendRouting: {
    description: 'Test frontend routing (Next.js pages)',
    test: async () => {
      const routes = ['/', '/auth/login', '/dashboard'];
      const results = await Promise.all(routes.map(async route => {
        try {
          const response = await axios.get(`${config.frontendUrl}${route}`, {
            validateStatus: () => true // Don't throw on 404
          });
          return {
            route,
            status: response.status,
            ok: response.status < 400
          };
        } catch (error) {
          return {
            route,
            status: 0,
            ok: false,
            error: error instanceof Error ? error.message : String(error)
          };
        }
      }));
      
      const failed = results.filter(r => !r.ok);
      if (failed.length > 0) {
        throw new Error(`Routing errors:\n${failed.map(f => 
          `- ${f.route}: ${f.status || f.error}`
        ).join('\n')}`);
      }
      return true;
    }
  },
  backendEndpoints: {
    description: 'Test backend API endpoints',
    test: async () => {
      const endpoints = [
        '/health',
        '/api/v1/auth/login',
        '/api/v1/auth/register'
      ];
      
      const results = await Promise.all(endpoints.map(async endpoint => {
        try {
          const response = await axios.get(`${config.backendUrl}${endpoint}`, {
            validateStatus: () => true
          });
          return {
            endpoint,
            status: response.status,
            ok: response.status < 500 // Allow 404 but not 500
          };
        } catch (error) {
          return {
            endpoint,
            status: 0,
            ok: false,
            error: error instanceof Error ? error.message : String(error)
          };
        }
      }));

      const failed = results.filter(r => !r.ok);
      if (failed.length > 0) {
        throw new Error(`API endpoint errors:\n${failed.map(f => 
          `- ${f.endpoint}: ${f.status || f.error}`
        ).join('\n')}`);
      }
      return true;
    }
  },
  authFlow: {
  description: 'Test authentication flow',
  test: async () => {
    try {
      // Test registration
      const registerResponse = await axios.post(
        `${config.backendUrl}/api/v1/auth/register`,
        {
          email: config.testUser.email,
          username: 'tester',
          password: config.testUser.password
        },
        {
          validateStatus: () => true // Don't throw on error status
        }
      );
      
      console.log('Registration response:', registerResponse.status, registerResponse.data);
      
      if (registerResponse.status >= 400) {
        throw new Error(`Registration failed: ${registerResponse.status} - ${JSON.stringify(registerResponse.data)}`);
      }

        // Test login
        const loginResponse = await axios.post(
          `${config.backendUrl}/api/v1/auth/login`,
          new URLSearchParams({
            username: config.testUser.email,
            password: config.testUser.password,
            grant_type: 'password'
          }),
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        );
        
        const loginData = loginResponse.data as { access_token?: string };
        if (!loginData.access_token) {
          throw new Error('Login failed: No token received');
        }
        
        return true;
      } catch (error) {
        if (typeof error === 'object' && error !== null) {
          const err = error as { response?: { data?: { detail?: string } }, message?: string };
          throw new Error(`Auth flow failed: ${err.response?.data?.detail || err.message}`);
        } else {
          throw new Error(`Auth flow failed: ${String(error)}`);
        }
      }
    }
  },
  corsConfiguration: {
    description: 'Test CORS configuration',
    test: async () => {
      try {
        const response = await axios.request({
          url: `${config.backendUrl}/api/v1/auth/login`,
          method: 'OPTIONS',
          headers: {
            'Origin': config.frontendUrl,
            'Access-Control-Request-Method': 'POST'
          }
        });
        
        if (!response.headers['access-control-allow-origin']) {
          throw new Error('Missing CORS headers');
        }
        
        return true;
      } catch (error) {
        throw new Error(`CORS test failed: ${typeof error === 'object' && error !== null && 'message' in error ? (error as any).message : String(error)}`);
      }
    }
  }
};

// Run all tests
async function runTests() {
  console.log('🚀 Starting Pink Coded Troubleshooter\n');
  
  let allPassed = true;
  
  for (const [name, test] of Object.entries(tests)) {
    try {
      console.log(`🔍 ${test.description}...`);
      const result = await test.test();
      console.log(`✅ ${name}: Passed\n`);
    } catch (error) {
      const errorMessage = (typeof error === 'object' && error !== null && 'message' in error)
        ? (error as { message: string }).message
        : String(error);
      console.error(`❌ ${name}: Failed - ${errorMessage}\n`);
      allPassed = false;
    }
  }
  
  console.log(allPassed 
    ? '🎉 All tests passed! Your setup looks good.'
    : '⚠ Some tests failed. Check the errors above.'
  );
  
  if (!allPassed) {
    console.log('\nRecommended fixes:');
    console.log('- Verify Docker containers are running: docker-compose ps');
    console.log('- Check frontend routes exist in app/ directory');
    console.log('- Ensure backend endpoints are properly registered in main.py');
    console.log('- Confirm CORS is configured for frontend URL');
    console.log('- Check network connectivity between containers');
  }
}

runTests();