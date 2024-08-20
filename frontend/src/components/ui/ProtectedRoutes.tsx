// src/components/ui/ProtectedRoutes.tsx

import React, { useEffect, useState } from 'react';
import { Navigate, Outlet, useNavigate } from 'react-router-dom';
import { getCookie } from '@/utils/cookieUtils';

const ProtectedRoutes: React.FC = () => {
    const [isAuth, setIsAuth] = useState<boolean>(false);
    const navigate=useNavigate()
    useEffect(() => {
        const authToken = getCookie('authToken');
        console.log('Auth Token:', authToken); // Add logging to check token value
        setIsAuth(!!authToken);
        navigate('/')
        if(authToken==null){
          navigate('/login')
        }
      
    }, []);

    return isAuth ? <Outlet /> : <Navigate to='/login' />;
};

export default ProtectedRoutes;
