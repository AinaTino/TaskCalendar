import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Link } from "react-router-dom";
import useUserStore from "@/store/UserStore";
import { useState } from "react";

const formSchema = z.object({
  username: z.string().min(2, {
    message: "L’e-mail ou le numéro de mobile entré n’est pas associé à un compte. Trouvez votre compte et connectez-vous.",
  }).max(50),
  password: z.string().min(2, {
  }).max(50),
});

const Signup: React.FC = () => {
  const { register } = useUserStore((state) => ({
    register: state.register
  }));
  
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  function onSubmit(data: z.infer<typeof formSchema>) {
    register(data)
      .then(() => {
        setSuccessMessage("Registration successful!");
        form.reset(); // Reset the form to default values
        
      })
      .catch((error) => {
        console.error("Registration failed", error);
      });
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-center my-56">
        <div className="w-[50%]">
          <h1 className="font-bold text-3xl mb-4 text-blue-600">Task Manager</h1>
          <p className="text-[22px] font-normal">Avec Task Manager, gerer votre emploi du temps avec efficacite</p>
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
              <Button className="bg-blue-600 w-full text-white capitalize text-[15px] font-semibold h-[50px]" type="submit">se connecter</Button>
            </form>
          </Form>

          {successMessage && (
            <div className="mt-4 text-green-600 font-semibold">{successMessage}</div>
          )}

          <div className="flex items-center justify-center my-4">
            <Button className="bg-green-600 text-white h-[50px] font-semibold text-md"><Link to='/login'> j'ai un compte</Link></Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
