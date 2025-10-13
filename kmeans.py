import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.cluster import KMeans
from matplotlib.ticker import MaxNLocator



def create_cluster_csv(num_clusters, images, x_values, y_values, decomposition_values, output_path='./static/clusters.csv'):
    rand = str(np.random.randint(1, 1024))
    output_path = str.replace(output_path, '.csv', rand+'.csv' )
    """
    Clusters the given data and saves the result to a CSV file.

    Parameters:
    - num_clusters: The number of clusters to form.
    - images: List of image names.
    - x_values: List of x values corresponding to the images.
    - y_values: List of y values corresponding to the images.
    - decomposition_values: List of decomposition values, each being a list of three [x, y] pairs.
    - output_path: Path to save the output CSV file (default is './static/clusters.csv').
    """
    data = pd.DataFrame({
        'image': images,
        'x': x_values,
        'y': y_values,
        'decomp1_x': [decomp[0][0] for decomp in decomposition_values],
        'decomp1_y': [decomp[0][1] for decomp in decomposition_values],
        'decomp2_x': [decomp[1][0] for decomp in decomposition_values],
        'decomp2_y': [decomp[1][1] for decomp in decomposition_values],
        'decomp3_x': [decomp[2][0] for decomp in decomposition_values],
        'decomp3_y': [decomp[2][1] for decomp in decomposition_values]
    })

    features = data[['x', 'y', 'decomp1_x', 'decomp1_y', 'decomp2_x', 'decomp2_y', 'decomp3_x', 'decomp3_y']].values

    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=300, n_init=10, random_state=42)
    data['cluster'] = kmeans.fit_predict(features)

    data = data[['cluster', 'image', 'x', 'y', 'decomp1_x', 'decomp1_y', 'decomp2_x', 'decomp2_y', 'decomp3_x', 'decomp3_y']]

    data.to_csv(output_path, index=False)



def create_cluster_csv_xy(num_clusters, images, x_values, y_values, output_path='./static/clusters.csv', plot_path='./static/cluster_plot.png'):
    rand = str(np.random.randint(1, 1024))
    output_path = output_path.replace('.csv', rand+'.csv')
    plot_path = plot_path.replace('.png', rand+'.png')

    data = pd.DataFrame({
        'image': images,
        'x': x_values,
        'y': y_values
    })

    features = data[['x', 'y']].values

    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=300, n_init=10, random_state=42)
    data['cluster'] = kmeans.fit_predict(features)

    data = data[['cluster', 'image', 'x', 'y']]

    data.to_csv(output_path, index=False)
    
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(data['x'], data['y'], c=data['cluster'], cmap='viridis')
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title('Distribuição de X e Y colorida por Cluster')
    plt.colorbar(scatter, ticks=range(num_clusters))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10)) 
    plt.grid(True)
    plt.savefig(plot_path)
    plt.close()



def plot_elbow_curve(images, x_values, y_values, decomposition_values, max_clusters=10, output_path='./static/elbow_curve.png'):
    """
    Plots the elbow curve to determine the optimal number of clusters and saves the plot to the specified directory.

    Parameters:
    - images: List of image names.
    - x_values: List of x values corresponding to the images.
    - y_values: List of y values corresponding to the images.
    - decomposition_values: List of decomposition values, each being a list of three [x, y] pairs.
    - max_clusters: Maximum number of clusters to be tested (default is 10).
    - output_path: Path to save the output plot (default is './static/elbow_curve.png').
    """
    data = pd.DataFrame({
        'image': images,
        'x': x_values,
        'y': y_values,
        'decomp1_x': [decomp[0][0] for decomp in decomposition_values],
        'decomp1_y': [decomp[0][1] for decomp in decomposition_values],
        'decomp2_x': [decomp[1][0] for decomp in decomposition_values],
        'decomp2_y': [decomp[1][1] for decomp in decomposition_values],
        'decomp3_x': [decomp[2][0] for decomp in decomposition_values],
        'decomp3_y': [decomp[2][1] for decomp in decomposition_values]
    })

    features = data[['x', 'y', 'decomp1_x', 'decomp1_y', 'decomp2_x', 'decomp2_y', 'decomp3_x', 'decomp3_y']].values

    # Calculate WCSS for different values of k
    wcss = []
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
        kmeans.fit(features)
        wcss.append(kmeans.inertia_)

    # Plot the elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_clusters + 1), wcss, marker='o', linestyle='--')
    plt.title('Elbow Curve')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.xticks(range(1, max_clusters + 1))
    plt.grid(True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path)
    plt.close()
