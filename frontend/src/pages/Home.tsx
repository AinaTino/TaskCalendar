import React from 'react';
import FullCalendar from '@fullcalendar/react';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Form, FormField, FormItem, FormControl, FormMessage } from "@/components/ui/form";
import Header from '@/components/Header';

const formSchema = z.object({
  taskName: z.string().min(1, "Task name is required."),
  taskDate: z.string().min(1, "Task date is required."),
});

const Home: React.FC = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      taskName: "",
      taskDate: "",
    },
  });

  function handleEventClick(info: any) {
    alert('Event: ' + info.event.title);
  }

  return (
    <div className="p-10">
      <Header/>
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        editable={true}
        selectable={true}
        events={[
          { title: 'Event 1', date: '2024-08-01' },
          { title: 'Event 2', date: '2024-08-02' }
        ]}
        eventClick={handleEventClick}
      />

      <div className="mt-10">
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline">Add Task</Button>
          </PopoverTrigger>
          <PopoverContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(() => {})} className="space-y-8">
                <FormField
                  control={form.control}
                  name="taskName"
                  render={({ field }) => (
                    <FormItem>
                      <Label htmlFor="taskName">Task Name</Label>
                      <FormControl>
                        <Input id="taskName" placeholder="Task Name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="taskDate"
                  render={({ field }) => (
                    <FormItem>
                      <Label htmlFor="taskDate">Task Date</Label>
                      <FormControl>
                        <Input id="taskDate" type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit">Save Task</Button>
              </form>
            </Form>
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};

export default Home;
