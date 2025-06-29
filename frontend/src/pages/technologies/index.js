import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>Технологии</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="Технологии" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <h3 className={styles.sectionTitle}>Backend:</h3>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Python 3.10
              </li>
              <li className={styles.textItem}>
                Django 4.2.1
              </li>
              <li className={styles.textItem}>
                Django REST Framework
              </li>
              <li className={styles.textItem}>
                Djoser (аутентификация)
              </li>
              <li className={styles.textItem}>
                PostgreSQL (база данных)
              </li>
              <li className={styles.textItem}>
                Pillow (обработка изображений)
              </li>
            </ul>
            
            <h3 className={styles.sectionTitle}>Frontend:</h3>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                React.js 17.0.1
              </li>
              <li className={styles.textItem}>
                React Router DOM
              </li>
              <li className={styles.textItem}>
                CSS Modules
              </li>
              <li className={styles.textItem}>
                React Helmet (SEO)
              </li>
            </ul>
            
            <h3 className={styles.sectionTitle}>Инфраструктура:</h3>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Docker & Docker Compose
              </li>
              <li className={styles.textItem}>
                Nginx (веб-сервер)
              </li>
              <li className={styles.textItem}>
                Git (версионирование)
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

