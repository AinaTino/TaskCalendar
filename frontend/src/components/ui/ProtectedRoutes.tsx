import useUserStore from '@/store/UserStore'
import React from 'react'
import { Navigate ,Outlet} from 'react-router-dom'

const ProtectedRoutes: React.FC = () => {
    const { users } = useUserStore((state) => ({
      users: state.users
    }));
  
    const isAuth = users.length > 0;
  
    console.log("isAuth:", isAuth); // Add this to debug
  
    return isAuth ? <Outlet /> : <Navigate to='/login' />;
  }
  

export default ProtectedRoutes