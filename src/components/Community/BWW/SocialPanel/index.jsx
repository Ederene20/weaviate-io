import React, { useState, useEffect } from 'react';
import projectsData from '/data/projects.json';
import styles from './styles.module.scss';
import Link from '@docusaurus/Link';

const ProjectFilter = () => {
  const [filteredProjects, setFilteredProjects] = useState(projectsData);
  const [showAll, setShowAll] = useState(false);
  const [type, setType] = useState('');
  const [category, setCategory] = useState('');
  const [model, setModel] = useState('');
  const [stack, setStack] = useState('');
  const [projectType, setProjectType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const uniqueTypes = Array.from(
    new Set(projectsData.flatMap((project) => project.types))
  );
  const uniqueCategories = Array.from(
    new Set(projectsData.flatMap((project) => project.category))
  );
  const uniqueModels = Array.from(
    new Set(projectsData.map((project) => project.models))
  );
  const uniqueStacks = Array.from(
    new Set(projectsData.map((project) => project.stack))
  );

  useEffect(() => {
    let filtered = projectsData.filter(
      (project) =>
        (project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          project.types
            .join(', ')
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          project.category
            .join(', ')
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          project.models.toLowerCase().includes(searchQuery.toLowerCase()) ||
          project.stack.toLowerCase().includes(searchQuery.toLowerCase())) &&
        (projectType ? project.type === projectType : true) &&
        (type ? project.types.includes(type) : true) &&
        (category ? project.category.includes(category) : true) &&
        (model ? project.models === model : true) &&
        (stack ? project.stack === stack : true)
    );
    setFilteredProjects(filtered);
  }, [projectType, type, category, model, stack, searchQuery]);

  const handleProjectTypeClick = (value) => {
    setProjectType((prev) => (prev === value ? '' : value));
  };

  return (
    <div className={styles.bg}>
      <div className="container">
        <div className={styles.title}>
          <h2>Weaviate projects</h2>
          <p>
            Discover the Latest AI Innovations: Dive into our comprehensive
            database showcasing diverse Community Projects and Show cases
            powered by Weaviate. Explore the forefront projects shaping the
            future landscape of artificial intelligence
          </p>
        </div>
        <div className={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search Projects"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div>
          <button
            className={styles.projectButton}
            onClick={() => handleProjectTypeClick('Community projects')}
          >
            Community projects
          </button>
          <button
            className={styles.projectButton}
            onClick={() => handleProjectTypeClick('Business projects')}
          >
            Business projects
          </button>
        </div>
        <div className={styles.tableContainer}>
          <table>
            <thead>
              <tr>
                <th>Project</th>
                <th>
                  <select onChange={(e) => setType(e.target.value)}>
                    <option value="">Type</option>
                    {uniqueTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </th>
                <th>
                  <select onChange={(e) => setCategory(e.target.value)}>
                    <option value="">Category</option>
                    {uniqueCategories.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </select>
                </th>
                <th>
                  <select onChange={(e) => setModel(e.target.value)}>
                    <option value="">Model(s)</option>
                    {uniqueModels.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </th>
                <th>
                  <select onChange={(e) => setStack(e.target.value)}>
                    <option value="">Stack</option>
                    {uniqueStacks.map((stack) => (
                      <option key={stack} value={stack}>
                        {stack}
                      </option>
                    ))}
                  </select>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredProjects
                .slice(0, showAll ? filteredProjects.length : 3)
                .map((project) => (
                  <tr key={project.id}>
                    <td>
                      <div className={styles.projectContainer}>
                        <Link className={styles.projectLink} to={project.link}>
                          {project.name}
                        </Link>
                        <span className={styles.projectTab}>
                          {project.type}
                        </span>
                      </div>
                    </td>
                    <td>{project.types.join(', ')}</td>
                    <td>{project.category.join(', ')}</td>
                    <td>{project.models}</td>
                    <td>{project.stack}</td>
                  </tr>
                ))}
            </tbody>
          </table>
          <div className={styles.buttons}>
            <button
              className={styles.buttonLine}
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? 'Show Less' : 'See All'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectFilter;
