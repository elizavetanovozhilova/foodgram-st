import {
  Container,
  Input,
  Main,
  Form,
  Button,
  FormTitle,
} from "../../components";
import styles from "./styles.module.css";
import { useFormWithValidation } from "../../utils";
import { AuthContext } from "../../contexts";
import { Redirect } from "react-router-dom";
import { useContext, useEffect } from "react";
import MetaTags from "react-meta-tags";
import { useHistory } from "react-router-dom";

const SignIn = ({ onSignIn, submitError, setSubmitError }) => {
  const { values, handleChange, errors } = useFormWithValidation();
  const authContext = useContext(AuthContext);
  const history = useHistory();

  useEffect(() => {
    if (authContext) {
      history.replace("/");
    }
  }, [authContext, history]);

  const onChange = (e) => {
    setSubmitError({ submitError: "" });
    handleChange(e);
  };

  return (
    <Main withBG asFlex>
      {/* {authContext && <Redirect to="/" />} */}
      <Container className={styles.center}>
        <MetaTags>
          <title>Войти на сайт</title>
          <meta
            name="description"
            content="Фудграм - Войти на сайт"
          />
          <meta property="og:title" content="Войти на сайт" />
        </MetaTags>
        <Form
          className={styles.form}
          onSubmit={(e) => {
            e.preventDefault();
            onSignIn(values);
          }}
        >
          <FormTitle>Войти</FormTitle>

          <Input
            required
            isAuth={true}
            name="email"
            placeholder="Email"
            onChange={onChange}
            error={errors}
          />
          <Input
            required
            isAuth={true}
            type="password"
            name="password"
            placeholder="Пароль"
            error={errors}
            submitError={submitError}
            onChange={onChange}
          />
          {/* <LinkComponent
            className={styles.link}
            href="/reset-password"
            title="Забыли пароль?"
          /> */}
          <Button modifier="style_dark" type="submit" className={styles.button}>
            Войти
          </Button>
          <a
            href="/auth/login/github/"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.githubButton}
            style={{
              display: 'block',
              marginTop: 16,
              textAlign: 'center',
              background: '#24292f',
              color: '#fff',
              padding: '12px 0',
              borderRadius: 6,
              textDecoration: 'none',
              fontWeight: 600,
              fontSize: 16,
              letterSpacing: 0.5,
              transition: 'background 0.2s',
            }}
          >
            <svg style={{verticalAlign: 'middle', marginRight: 8}} height="24" width="24" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.19 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>
            Войти через GitHub
          </a>
        </Form>
      </Container>
    </Main>
  );
};

export default SignIn;
