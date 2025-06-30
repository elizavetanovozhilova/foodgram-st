import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';

const OAuthSuccess = () => {
  const history = useHistory();
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('token', token);
    }
    history.replace('/');
  }, [history]);
  return null;
};

export default OAuthSuccess; 