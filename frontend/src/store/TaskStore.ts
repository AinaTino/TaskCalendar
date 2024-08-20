import {create} from 'zustand'
interface TaskProps{
    title:string;
    date:string;
}
interface Task{
    task:TaskProps[]
}
const TaskStores=create<Task>((set)=>({
    

}))

export default TaskStores