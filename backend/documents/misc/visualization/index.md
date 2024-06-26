# Visualization


Data in a Polars `DataFrame` can be visualized using common visualization libraries.


We illustrate plotting capabilities using the Iris dataset. We scan a CSV and then do a group-by on the `species` column and get the mean of the `petal_length`.


 Python



```python

import polars as pl

path = "docs/data/iris.csv"

df = pl.scan_csv(path).group_by("species").agg(pl.col("petal_length").mean()).collect()
print(df)

```







## Built-in plotting with hvPlot


Polars has a `plot` method to create interactive plots using [hvPlot](https://hvplot.holoviz.org/).


 Python



```python

df.plot.bar(
    x="species",
    y="petal_length",
    width=650,
)

```








hvplot\_bar

 





 






## Matplotlib


To create a bar chart we can pass columns of a `DataFrame` directly to Matplotlib as a `Series` for each column. Matplotlib does not have explicit support for Polars objects but Matplotlib can accept a Polars `Series` because it can convert each Series to a numpy array, which is zero-copy for numeric
data without null values.


 Python



```python

import matplotlib.pyplot as plt

plt.bar(x=df["species"], height=df["petal_length"])

```




![](data:image/png;base64, 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Vpx++uk7fOzJJ5+MqqqqePbZZ/f4665duzbOOOOMPb5dPvt++ctfxje+8Y046KCDorq6Onr16hXDhw+PBQsW7NLz99Q/3Hx27cpx8Wtf+1qb35b9fR133HGxdu3aj/VDxbfddlvMnDlzt1+bPFL/DAw7Nn78+Bg1alT84he/iL59+7Z5bMaMGTF06NAYOHDgx9rm1q1bo1OnTr91nZ39DyyVsisz88kwatSo2Lp1a/zLv/xLHHLIIfHmm2/GY489Fhs2bKj0aHxG7Inj4q4eUzp16vSxj4fZ/1cLfg8FPuI3v/lN6dmzZ7nhhhvaLN+0aVOpqakp06ZNK08++WT58pe/XDp37lz69u1bJkyYUDZv3ty67sEHH1z+7u/+rpx//vmltra2jB07tjQ3N5dLL7209OrVq1RXV5eDDjqo/P3f/33rcyKizJ07t/X+mjVryrnnnlv233//0rVr1zJkyJCyaNGi1sf/6Z/+qRxyyCFl3333LYcffni566672sz70e09++yz5aSTTiqdO3cu3bt3LxdddFHZtGlT6+Njx44tI0aMKDfeeGPp3bt36dev3+6+lewFv/rVr0pElPnz5//WdcaPH18OOOCAUltbW0466aTS2NhYSillxowZJSLa3GbMmFFKKeX1118vf/qnf1q6detWamtry9lnn13WrVvXut3GxsZy4oknlpqamlJbW1sGDx5clixZUkop5a233irnnntu6dOnT+nSpUs5+uijy6xZs9rvjaBd7cpx8brrriuDBg1qfWxnx5QFCxaUQYMGlerq6jJkyJAyd+7cEhHlmWeeKaWUMm/evBIR5Ve/+lUp5f19tL6+vjz00EPliCOOKN26dSvDhw8vb7zxxnav9YFt27aVf/iHfyiHHnpo6dSpU2loaCg33nhj6+NXXnllOeyww0qXLl3K5z//+XLNNdeUrVu37tk3jU80l4DZTseOHeOCCy6ImTNnRvnQz0TOmTMntm3bFsOGDYvTTz89Ro0aFc8++2zMnj07/ud//icuu+yyNtu5+eabY9CgQfHMM8/EtddeG7fffnvcf//98R//8R+xcuXKuPvuu6Nfv347nGHz5s1xwgknxP/+7//G/fffH8uXL48rr7wyWlpaIiJi7ty58c1vfjMuv/zyeP755+OSSy6JcePGxbx583a4vS1btsTw4cNj//33jyVLlsScOXPiJz/5yXYzP/bYY7Fy5cp49NFH44EHHtiNd5G9paamJmpqauK+++6L5ubmHa5z9tlnx/r16+PHP/5xLF26NAYPHhynnHJKvP322zF69Oi4/PLL46ijjoq1a9fG2rVrY/To0dHS0hIjRoyIt99+Ox5//PF49NFH4+c//3mMHj26dbtjxoyJvn37xpIlS2Lp0qVx1VVXxb777hsREe+9914MGTIkHnzwwXj++efj4osvjvPPPz8WL168V94X9qzfdVw877zzdvi8jx5Tmpqa4qyzzopjjjkmli1bFjfccENMmjTpd77+r3/967j55pvjX//1X+OJJ56I1atXx7e//e2drj958uSYOnVqXHvttfHiiy/GrFmz2vwnB7W1tTFz5sx48cUX47bbbovp06fHrbfe+jHeET71Kl2gfDKtWLGiRESZN29e67KvfOUr5etf/3oZP358ufjii9us/+STT5YOHTqUd999t5Ty/hnAkSNHtllnwoQJ5eSTTy4tLS07fM340Bm7O++8s9TW1pYNGzbscN3jjjuuXHTRRW2WnX322eWrX/3qDrf3/e9/v+y///5tzlI++OCDpUOHDq1ndMaOHVt69uxZmpubd/Ku8En1n//5n2X//fcvnTt3Lscdd1yZPHlyWb58eSnl/X2zrq6uvPfee22ec+ihh5Y777yzlFK2O3NTSimPPPJI2Weffcrq1atbl73wwgslIsrixYtLKaXU1taWmTNn7vKcZ555Zrn88st/nz+RT4DfdlwsZfv9aEfHlGnTppUePXq0HitLKWX69Om/8wxgRJRXXnml9Tl33HFH6dmzZ5vX+uAMYFNTU6muri7Tp0/f5b/tu9/9bhkyZMgur8+nnzOA7NARRxwRxx13XPzwhz+MiIhXXnklnnzyyRg/fnwsX748Zs6c2XrmpaamJoYPHx4tLS2xatWq1m0MHTq0zTYvvPDCaGxsjP79+8df//VfxyOPPLLT129sbIw//MM/jO7du+/w8RUrVsTxxx/fZtnxxx8fK1as2On6gwYNim7durVZv6WlJVauXNm67JhjjvG5v0+hUaNGxRtvvBH3339/nH766TF//vwYPHhwzJw5M5YvXx6bN2+OHj16tNlnV61aFa+++upOt7lixYpoaGiIhoaG1mUDBgyI/fbbr3U/mzhxYvzVX/1VnHrqqTF16tQ229u2bVvccMMNccwxx0T37t2jpqYmHn744Vi9enX7vRG0q992XNyZjx5TVq5cGQMHDozOnTu3LvviF7/4O1+7a9euceihh7be7927d6xfv36H665YsSKam5vjlFNO2en2Zs+eHccff3z06tUrampq4pprrrFvJiMA2anx48fHvffeG5s2bYoZM2bEoYceGieccEJs3rw5LrnkkmhsbGy9LV++PF5++eU2B6gPx1ZExODBg2PVqlVxww03xLvvvhvnnHNO/Pmf//kOX7tLly7t+rftzEdn5tOjc+fOcdppp8W1114bCxcujAsvvDCuu+662Lx5c/Tu3bvN/trY2BgrV66MK664Yrde8/rrr48XXnghzjzzzPjv//7vGDBgQMydOzciIr773e/GbbfdFpMmTYp58+ZFY2NjDB8+PLZu3bon/lwqZGfHxZ3ZU8eUDz5a8IGqqqo2l6I/7HcdP5966qkYM2ZMfPWrX40HHnggnnnmmbj66qvtm8kIQHbqnHPOiQ4dOsSsWbPirrvuir/8y7+MqqqqGDx4cLz44ovxhS98Ybvb7zp7VldXF6NHj47p06fH7Nmz495774233357u/UGDhwYjY2NO3wsIuLII4/c7ic+FixYEAMGDNjp+suXL48tW7a0Wb9Dhw7Rv3//3/VW8Ck0YMCA2LJlSwwePDjWrVsXHTt23G5/PeCAAyLi/W9dbtu2rc3zjzzyyFizZk2sWbOmddmLL74Y77zzTpv97PDDD4+/+Zu/iUceeSS+9rWvxYwZMyLi/f1rxIgR8fWvfz0GDRoUhxxySPzsZz/bC3857Wlnx8Vd1b9//3juuefafF51yZIle3TGww47LLp06bLTn6RZuHBhHHzwwXH11VfH0KFD47DDDovXX399j87AJ58AZKdqampi9OjRMXny5Fi7dm1ceOGFERExadKkWLhwYVx22WXR2NgYL7/8cvzoRz/a7gsVH3XLLbfEv//7v8dLL70UP/vZz2LOnDnRq1ev2G+//bZb97zzzotevXrFyJEjY8GCBfHzn/887r333njqqaciIuKKK66ImTNnxrRp0+Lll1+OW265Jf7rv/5rpx+KHjNmTHTu3DnGjh0bzz//fMybNy8mTJgQ559/fpsPRvPps2HDhjj55JPj3/7t3+LZZ5+NVatWxZw5c+If//EfY8SIEXHqqafGsGHDYuTIkfHII4/Ea6+9FgsXLoyrr746nn766YiI6NevX6xatSoaGxvjrbfeiubm5jj11FPjmGOOiTFjxsSyZcti8eLFccEFF8QJJ5wQQ4cOjXfffTcuu+yymD9/frz++uuxYMGCWLJkSRx55JER8f4/wo8++mgsXLgwVqxYEZdcckm8+eablXyr2AN2dlzcVX/xF38RLS0tcfHFF8eKFSvi4Ycfjptvvjki4mOF5G/TuXPnmDRpUlx55ZVx1113xauvvhqLFi2KH/zgBxHx/r65evXquOeee+LVV1+N22+/vfXMNYlU+kOIfLItXLiwRESbL1eUUsrixYvLaaedVmpqakq3bt3KwIEDy0033dT6+MEHH1xuvfXWNs/5/ve/X4499tjSrVu3UldXV0455ZSybNmy1sfjIz/b8tprr5VRo0aVurq60rVr1zJ06NDy05/+tPXx9voZGD5d3nvvvXLVVVeVwYMHl/r6+tK1a9fSv3//cs0115Rf//rXpZT3PxQ/YcKE0qdPn7LvvvuWhoaGMmbMmNYveLz33ntl1KhRZb/99tvln4Fpbm4u5557bmloaCidOnUqffr0KZdddlnrh/s3bNhQRowYUWpqasqBBx5YrrnmmnLBBRfYxz4DdnZc3NnPwHzUggULysCBA0unTp3KkCFDyqxZs0pElJdeeqmUsvOfgfmwD346ZmevtW3btnLjjTeWgw8+uOy7777b/ezWFVdcUXr06FFqamrK6NGjy6233rrda/DZVlXKTj5EAAC0u7vvvjvGjRsXGzdurNjnn8nH/wQCAHvRXXfdFYccckj8wR/8QSxfvjwmTZoU55xzjvhjrxKAALAXrVu3Lr7zne/EunXronfv3nH22WfHTTfdVOmxSMYlYACAZHwLGAAgGQEIAJCMAAQASEYAAgAkIwABAJIRgAAAyQhAAIBkBCAAQDICEAAgGQEIAJCMAAQASEYAAgAkIwABAJIRgAAAyQhAAIBkBCAAQDICEAAgGQEIAJCMAAQASEYAAgAkIwABAJIRgAAAyQhAAIBkBCAAQDICEAAgGQEIAJCMAAQASEYAAgAk839ep3DyWRnrcwAAAABJRU5ErkJggg==)


## Seaborn, Plotly & Altair


[Seaborn](https://seaborn.pydata.org/), [Plotly](https://plotly.com/) & [Altair](https://altair-viz.github.io/) can accept a Polars `DataFrame` by leveraging the [dataframe interchange protocol](https://data-apis.org/dataframe-api/), which offers zero-copy conversion where possible.


### Seaborn


 Python



```python

import seaborn as sns
sns.barplot(
    df,
    x="species",
    y="petal_length",
)

```




![](data:image/png;base64, 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pKWlGWOMmTlzppFU4DZz5kxjjDGHDx82Xbt2NeXKlTOhoaGmZ8+e5tixY/79pqWlmfvvv9+EhISY0NBQExsbazZv3myMMebHH380vXv3NjVq1DDBwcHmrrvuMnPmzCm+FwK31NW8b44ePdrExMT4113uPWft2rUmJibGeL1eExcXZxYsWGAkmW3bthljjFmxYoWRZE6fPm2M+emYDQ8PN0uWLDGNGzc25cqVMx07djTff/99oef6WV5envn3f/93c+edd5rAwEATGRlpxo8f71//8ssvmwYNGpjg4GBTt25dM3LkSHPx4sWb+6KhROESMBQQEKC+ffsqNTVV5hc/C/nhhx8qLy9PLVu21MMPP6wePXpo+/btmjdvnv73f/9XQ4YMKbCfSZMmKSYmRtu2bdOoUaP09ttv69NPP9X//M//aO/evfrggw9Up06dImfIyclR27ZtdeTIEX366adKT0/Xyy+/rPz8fEnSggUL9Nxzz+nFF1/Uzp079cwzz6h///5asWJFkfvLzc1Vx44dFRERoc2bN+vDDz/Ul19+WWjm5cuXa+/evVq2bJkWLVp0A68inBISEqKQkBAtXLhQPp+vyG169uyp48ePa/HixdqyZYtiY2PVrl07nTp1Sr169dKLL76oZs2a6ejRozp69Kh69eql/Px8devWTadOndKqVau0bNkyfffdd+rVq5d/v/Hx8apZs6Y2b96sLVu26JVXXlGZMmUkSRcuXFBcXJw+//xz7dy5U08//bQef/xxbdq06Za8LiheV3rf7NOnT5GP+/V7TnZ2trp06aKoqCht3bpV48aN04gRI674/OfOndOkSZP0X//1X1q9erUyMjL00ksvXXb7xMRETZw4UaNGjdKuXbs0Z86cAn/0IDQ0VKmpqdq1a5feeustTZ8+XVOmTLmGVwSu43SBomTYvXu3kWRWrFjhX9amTRvz2GOPmQEDBpinn366wPZr1qwxpUqVMufPnzfG/HQGsHv37gW2GTp0qHnwwQdNfn5+kc+pX5yxmzZtmgkNDTUnT54scttWrVqZp556qsCynj17mj/84Q9F7u+9994zERERBc5Sfv7556ZUqVL+MzgJCQmmatWqxufzXeZVgVvMnz/fREREmKCgINOqVSuTmJho0tPTjTE/HathYWHmwoULBR5z5513mmnTphljTKEzNcYYs3TpUlO6dGmTkZHhX/bNN98YSWbTpk3GGGNCQ0NNamrqVc/ZuXNn8+KLL17PPxEl0G+9bxpT+Lgq6j0nJSXFVKxY0f9eaowx06dPv+IZQElm//79/se88847pmrVqgWe6+czgNnZ2cbr9Zrp06df9b/tz3/+s4mLi7vq7eE+nAGEJKlx48Zq1aqV3n//fUnS/v37tWbNGg0YMEDp6elKTU31n2kJCQlRx44dlZ+fr4MHD/r30aJFiwL77Nevn9LS0tSoUSM9++yzWrp06WWfPy0tTc2bN1eFChWKXL979261bt26wLLWrVtr9+7dl90+JiZG5cqVK7B9fn6+9u7d618WFRXF5/5uAz169ND333+vTz/9VA8//LBWrlyp2NhYpaamKj09XTk5OapYsWKBY/jgwYM6cODAZfe5e/duRUZGKjIy0r+sadOmKl++vP+4GzZsmJ588km1b99eEydOLLC/vLw8jRs3TlFRUapQoYJCQkL0xRdfKCMjo/heCNxSv/W+eTm/fs/Zu3evoqOjFRQU5F92zz33XPG5y5YtqzvvvNN/v3r16jp+/HiR2+7evVs+n0/t2rW77P7mzZun1q1bq1q1agoJCdHIkSM5Vm9zBCD8BgwYoI8++khnz57VzJkzdeedd6pt27bKycnRM888o7S0NP8tPT1d+/btK/AG9MvYkqTY2FgdPHhQ48aN0/nz5/Xoo4/qT3/6U5HPHRwcXKz/tsv59cxwr6CgIHXo0EGjRo3SunXr1K9fP40ePVo5OTmqXr16geM3LS1Ne/fu1fDhw2/oOV9//XV988036ty5s7766is1bdpUCxYskCT9+c9/1ltvvaURI0ZoxYoVSktLU8eOHXXx4sWb8c9FCXG5983LuVnvOT9/1OBnHo+nwKXoX7rS++v69esVHx+vP/zhD1q0aJG2bdum1157jWP1NkcAwu/RRx9VqVKlNGfOHM2ePVtPPPGEPB6PYmNjtWvXLtWvX7/Q7Upnz8LCwtSrVy9Nnz5d8+bN00cffaRTp04V2i46OlppaWlFrpOkJk2aFPpJj7Vr16pp06aX3T49PV25ubkFti9VqpQaNWp0pZcCt4GmTZsqNzdXsbGxOnbsmAICAgodv5UqVZL007cs8/LyCjy+SZMmyszMVGZmpn/Zrl27dObMmQLHXcOGDfXCCy9o6dKl+uMf/6iZM2dK+ul469atmx577DHFxMSoXr16+vbbb2/Bvxy30uXeN69Wo0aNtGPHjgKfX928efNNnbFBgwYKDg6+7E/SrFu3TrVr19Zrr72mFi1aqEGDBjp8+PBNnQElDwEIv5CQEPXq1UuJiYk6evSo+vXrJ0kaMWKE1q1bpyFDhigtLU379u3TJ598UugLFb82efJk/fd//7f27Nmjb7/9Vh9++KGqVaum8uXLF9q2T58+qlatmrp37661a9fqu+++00cffaT169dLkoYPH67U1FSlpKRo3759mjx5sj7++OPLfug5Pj5eQUFBSkhI0M6dO7VixQoNHTpUjz/+eIEPPsP9Tp48qQcffFB/+9vftH37dh08eFAffvih3nzzTXXr1k3t27dXy5Yt1b17dy1dulSHDh3SunXr9Nprr+nrr7+WJNWpU0cHDx5UWlqafvzxR/l8PrVv315RUVGKj4/X1q1btWnTJvXt21dt27ZVixYtdP78eQ0ZMkQrV67U4cOHtXbtWm3evFlNmjSR9NP/dJctW6Z169Zp9+7deuaZZ/TDDz84+VKhGFzuffNq/du//Zvy8/P19NNPa/fu3friiy80adIkSbqmkPwtQUFBGjFihF5++WXNnj1bBw4c0IYNGzRjxgxJPx2rGRkZmjt3rg4cOKC3337bfyYbtzGnP4SIkmXdunVGUoEvVxhjzKZNm0yHDh1MSEiIKVeunImOjjYTJkzwr69du7aZMmVKgce899575u677zblypUzYWFhpl27dmbr1q3+9frVz7YcOnTI9OjRw4SFhZmyZcuaFi1amI0bN/rXF9fPwMDdLly4YF555RUTGxtrwsPDTdmyZU2jRo3MyJEjzblz54wxP30IfujQoaZGjRqmTJkyJjIy0sTHx/u/4HHhwgXTo0cPU758+av+GRifz2d69+5tIiMjTWBgoKlRo4YZMmSI/8P8J0+eNN26dTMhISGmSpUqZuTIkaZv374cc7ehy71vXu5nYH5t7dq1Jjo62gQGBpq4uDgzZ84cI8ns2bPHGHP5n4H5pZ9/OuZyz5WXl2fGjx9vateubcqUKVPoZ7mGDx9uKlasaEJCQkyvXr3MlClTCj0Hbi8eYy7zoQEAAHDLffDBB+rfv7+ysrIc+3w0bn/8JRAAABw0e/Zs1atXT3fccYfS09M1YsQIPfroo8QfihUBCACAg44dO6akpCQdO3ZM1atXV8+ePTVhwgSnx8JtjkvAAAAAluFbwAAAAJYhAAEAACxDAAIAAFiGAAQAALAMAQgA16Ffv37q3r2702MAwHXhW8AAcB2ysrJkjCnyTxsCQElHAAIAAFiGS8AAXGv+/PmKiopScHCwKlasqPbt2ys3N9d/eXbMmDGqXLmywsLCNHDgQF28eNH/2Pz8fCUnJ6tu3boKDg5WTEyM5s+fX2D/33zzjf71X/9VYWFhCg0NVZs2bXTgwAFJhS8BX2l/p0+fVnx8vCpXrqzg4GA1aNBAM2fOLN4XCAAug78EAsCVjh49qj59+ujNN9/UI488orNnz2rNmjX6+aLG8uXLFRQUpJUrV+rQoUPq37+/Klas6P8LC8nJyfrb3/6md999Vw0aNNDq1av12GOPqXLlymrbtq2OHDmi++67T/fff7+++uorhYWFae3atfrnP/9Z5DxX2t+oUaO0a9cuLV68WJUqVdL+/ft1/vz5W/Z6AcAvcQkYgCtt3bpVcXFxOnTokGrXrl1gXb9+/fTZZ58pMzNTZcuWlSS9++67Gj58uLKysnTp0iVVqFBBX375pVq2bOl/3JNPPqlz585pzpw5evXVVzV37lzt3btXZcqUKfT8/fr105kzZ7Rw4UL5fL4r7q9r166qVKmS3n///WJ6RQDg6nEGEIArxcTEqF27doqKilLHjh310EMP6U9/+pMiIiL863+OP0lq2bKlcnJylJmZqZycHJ07d04dOnQosM+LFy+qefPmkqS0tDS1adOmyPj7tf37919xf4MGDVKPHj20detWPfTQQ+revbtatWp1Q68BAFwvAhCAK5UuXVrLli3TunXrtHTpUv31r3/Va6+9po0bN17xsTk5OZKkzz//XHfccUeBdV6vV5IUHBx81bNczf46deqkw4cP6+9//7uWLVumdu3aafDgwZo0adJVPw8A3CwEIADX8ng8at26tVq3bq2kpCTVrl1bCxYskCSlp6fr/Pnz/pDbsGGDQkJCFBkZqQoVKsjr9SojI0Nt27Ytct/R0dGaNWuWLl26dMWzgE2bNr3i/iSpcuXKSkhIUEJCgtq0aaPhw4cTgAAcQQACcKWNGzdq+fLleuihh1SlShVt3LhRJ06cUJMmTbR9+3ZdvHhRAwYM0MiRI3Xo0CGNHj1aQ4YMUalSpRQaGqqXXnpJL7zwgvLz83XvvfcqKytLa9euVVhYmBISEjRkyBD99a9/Ve/evZWYmKjw8HBt2LBB99xzjxo1alRglqvZX1JSkuLi4tSsWTP5fD4tWrRITZo0cejVA2A7AhCAK4WFhWn16tWaOnWqsrOzVbt2bf3lL39Rp06dNG/ePLVr104NGjTQfffdJ5/Ppz59+uj111/3P37cuHGqXLmykpOT9d1336l8+fKKjY3Vq6++KkmqWLGivvrqKw0fPlxt27ZV6dKldffdd6t169ZFznOl/QUGBioxMVGHDh1ScHCw2rRpo7lz5xb76wQAReFbwABuO7/8hi4AoDB+CBoAAMAyBCAAAIBluAQMAABgGc4AAgAAWIYABAAAsAwBCAAAYBkCEAAAwDIEIAAAgGUIQAAAAMsQgAAAAJYhAAEAACxDAAIAAFjm/wDNHYHZb5N8bwAAAABJRU5ErkJggg==)


### Plotly


 Python



```python

import plotly.express as px

px.bar(
    df,
    x="species",
    y="petal_length",
    width=400,
)

```




 
   
### Altair


 Python



```python

import altair as alt

alt.Chart(df, width=700).mark_bar().encode(x="species:N", y="petal_length:Q")

```