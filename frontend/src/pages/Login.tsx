// src/pages/Login.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormField, FormItem, FormControl, FormMessage } from '@/components/ui/form';
import { Link, useNavigate } from 'react-router-dom';
import useUserStore from '@/store/UserStore';
import { useCookies } from 'react-cookie';

const formSchema = z.object({
  username: z.string().min(2, "Username is required").max(50),
  password: z.string().min(2, "Password is required").max(50),
});

const Login: React.FC = () => {
  const { authLogin } = useUserStore((state) => ({
    authLogin: state.authLogin
  }));
  const navigate = useNavigate();
  const [cookies, setCookie] = useCookies(['authToken']);
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const response = await authLogin(values);
      console.log('Login response:', response); // Log the response to check its structure
      
      // Assuming the token is stored in response.data.token
      const token = response?.data?.token;
      if (token) {
        setCookie('authToken', token, { path: '/' }); // Set the cookie
        setMessage("Login successful!");
        setMessageType('success');
        setTimeout(() => {
          navigate("/"); // Navigate to the home page
        }, 1000);
      } else {
        throw new Error("Token not found in the response");
      }
    } catch (error) {
      setMessage("Login failed. Please try again.");
      setMessageType('error');
      console.error("Login failed", error);
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-center my-56">
        <div className="w-[50%]">
          <h1 className="font-bold text-3xl mb-4 text-blue-600">Task Manager</h1>
          <p className="text-[22px] font-normal">Avec Task Manager, gérez votre emploi du temps avec efficacité</p>
        </div>
        <div className="w-[30%] border p-5 shadow-lg rounded-md bg-white">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input placeholder="Username" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input placeholder="Password" {...field} type="password" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button className="bg-blue-600 w-full text-white capitalize text-[15px] font-semibold h-[50px]" type="submit">Se connecter</Button>
            </form>
          </Form>

          {message && (
            <div className={`mt-4 font-semibold ${messageType === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {message}
            </div>
          )}

          <div className="flex items-center justify-center my-5">
            <Button className="bg-green-600 text-white h-[50px] font-semibold text-md">
              <Link to='/register'>Créer un nouveau compte</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
